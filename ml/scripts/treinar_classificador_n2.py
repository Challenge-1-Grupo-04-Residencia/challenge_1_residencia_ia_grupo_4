#!/usr/bin/env python
"""Treina o classificador estilístico da camada N2 (S-06, RF-21).

Roda da raiz do repositório:

    uv run python ml/scripts/treinar_classificador_n2.py

Grava ``backend/src/infrastructure/ml_models/classificador_n2.joblib`` e imprime as
métricas honestas — inclusive as de generalização, que são as que importam.

## Por que este script existe, em vez de só o notebook

A auditoria de 05/10 mediu o modelo que estava em produção contra os corpora e achou
97,6% de acurácia em ``fake-br`` e 95,9% em ``FakeRecogna``. Os dois são **datasets de
treino** daquele modelo, então o número não dizia nada sobre generalização. Fora do
treino o desempenho era 75,9% em ``faketrue-br`` e **48,9% em ``fakewhatsapp-br``** —
moeda, justamente no canal onde a desinformação circula.

Duas decisões saíram disso, e as duas estão aqui e não no notebook, para poderem ser
repetidas:

1. **Acentos são normalizados.** Nos corpora, o texto falso costuma vir sem acentuação e
   o verdadeiro acentuado; só a taxa de acentos por letra separa as classes com AUC de
   0,57 a 0,71. Um modelo que aprende isso é um detector de diacrítico, não de estilo, e
   desmonta no primeiro texto real sem acento. ``strip_accents="unicode"`` fecha o atalho.
2. **A avaliação é *leave-one-dataset-out*.** Validação aleatória dentro do mesmo corpus
   mede memorização de assunto; deixar um corpus inteiro de fora mede o que o produto
   vai encontrar em campo.
"""

import sys
import time
import unicodedata
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "backend"))

from src.infrastructure.search.tfidf_search import STOPWORDS_PT  # noqa: E402

DIRETORIO_DATASETS = RAIZ / "datasets"
CAMINHO_SAIDA = (
    RAIZ / "backend" / "src" / "infrastructure" / "ml_models" / "classificador_n2.joblib"
)

#: Corpora usados. ``fakenewsbr-v6`` fica fora por desequilíbrio (66 mil falsas contra
#: 231 mil verdadeiras) e por sobreposição com os demais: incluí-lo fazia o modelo
#: aprender a proporção do dataset em vez do estilo do texto.
CORPORA = (
    "fake-br",
    "FakeRecogna",
    "faketrue-br",
    "fakewhatsapp-br",
    "faketweet-br",
)

#: Teto por corpus, para que o maior não domine o treino.
MAXIMO_POR_CORPUS = 12_000
MINIMO_DE_PALAVRAS = 10
SEMENTE = 42


def sem_acento(palavra: str) -> str:
    """Remove diacríticos, para a stopword casar com o texto já normalizado."""
    decomposto = unicodedata.normalize("NFD", palavra)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


#: As stopwords precisam passar pela mesma normalização que o vetorizador aplica ao
#: texto. Sem isto, "não", "já" e "também" nunca casavam — o ``strip_accents`` já havia
#: transformado o texto em "nao", "ja", "tambem", e as versões acentuadas da lista
#: ficavam sem efeito (é o que o ``UserWarning`` do scikit-learn avisava).
STOPWORDS_NORMALIZADAS = sorted({sem_acento(p) for p in STOPWORDS_PT})


def carregar() -> pd.DataFrame:
    """Lê os corpora padronizados e devolve um quadro com texto, rótulo e origem."""
    partes = []
    for slug in CORPORA:
        caminho = DIRETORIO_DATASETS / slug / "padronizado.parquet"
        if not caminho.exists():
            print(f"  [aviso] {slug} não encontrado — rode ml/scripts/baixar_datasets.sh")
            continue
        quadro = pd.read_parquet(caminho)
        quadro = quadro[quadro["rotulo"].isin(["falso", "verdadeiro"])]
        quadro = quadro.dropna(subset=["texto"])
        quadro = quadro[quadro["texto"].str.split().str.len() >= MINIMO_DE_PALAVRAS]
        if len(quadro) > MAXIMO_POR_CORPUS:
            quadro = quadro.sample(MAXIMO_POR_CORPUS, random_state=SEMENTE)
        quadro = quadro[["texto", "rotulo"]].copy()
        quadro["corpus"] = slug
        partes.append(quadro)
        print(f"  {slug:20} {len(quadro):6} linhas")
    if not partes:
        raise SystemExit("nenhum corpus disponível: rode ml/scripts/baixar_datasets.sh")
    return pd.concat(partes, ignore_index=True)


def montar_modelo() -> Pipeline:
    """O classificador: TF-IDF de palavras e bigramas, mais regressão logística.

    ``strip_accents="unicode"`` é a peça que impede o modelo de resolver a tarefa pelo
    atalho do diacrítico — ver o cabeçalho do módulo.
    """
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    strip_accents="unicode",
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=5,
                    max_features=80_000,
                    sublinear_tf=True,
                    stop_words=STOPWORDS_NORMALIZADAS,
                ),
            ),
            (
                "classificador",
                LogisticRegression(
                    max_iter=2000,
                    C=4.0,
                    class_weight="balanced",
                    random_state=SEMENTE,
                ),
            ),
        ]
    )


def _metricas(modelo: Pipeline, textos, rotulos) -> tuple[float, float]:
    indice = list(modelo.classes_).index("verdadeiro")
    probabilidade = modelo.predict_proba(textos)[:, indice]
    verdadeiro = (rotulos == "verdadeiro").to_numpy()
    return (
        accuracy_score(rotulos, modelo.predict(textos)),
        roc_auc_score(verdadeiro, probabilidade),
    )


def avaliar_generalizacao(dados: pd.DataFrame) -> None:
    """*Leave-one-dataset-out*: treina sem um corpus e mede nele.

    É o número que diz o que esperar em campo. Acurácia dentro do próprio corpus de
    treino não mede generalização — foi o erro que deixou um modelo de 48,9% em WhatsApp
    passar por um modelo de 97%.
    """
    print("\n--- generalização (treina sem o corpus, mede nele) ---")
    print(f"{'corpus de fora':20}{'n':>7}{'acurácia':>10}{'AUC':>8}")
    for slug in dados["corpus"].unique():
        treino = dados[dados["corpus"] != slug]
        teste = dados[dados["corpus"] == slug]
        if teste["rotulo"].nunique() < 2 or len(teste) < 50:
            print(f"{slug:20}{len(teste):7}  (amostra insuficiente)")
            continue
        modelo = montar_modelo().fit(treino["texto"], treino["rotulo"])
        acuracia, auc = _metricas(modelo, teste["texto"], teste["rotulo"])
        print(f"{slug:20}{len(teste):7}{acuracia * 100:9.1f}%{auc:8.3f}")


def main() -> None:
    inicio = time.monotonic()
    print("Carregando corpora:")
    dados = carregar()
    print(f"  total {len(dados)} linhas, {dados['rotulo'].value_counts().to_dict()}")

    avaliar_generalizacao(dados)

    # Divisão estratificada por corpus **e** rótulo: sem isso um corpus inteiro podia
    # cair só no teste, e a métrica misturava erro de amostragem com erro do modelo.
    treino, teste = train_test_split(
        dados,
        test_size=0.2,
        random_state=SEMENTE,
        stratify=dados["corpus"] + "|" + dados["rotulo"],
    )
    modelo = montar_modelo().fit(treino["texto"], treino["rotulo"])

    print("\n--- dentro do domínio (20% separados de cada corpus) ---")
    acuracia, auc = _metricas(modelo, teste["texto"], teste["rotulo"])
    print(f"  geral: acurácia {acuracia * 100:.1f}%  AUC {auc:.3f}")
    for slug in teste["corpus"].unique():
        parte = teste[teste["corpus"] == slug]
        if parte["rotulo"].nunique() < 2:
            continue
        acuracia_corpus, auc_corpus = _metricas(modelo, parte["texto"], parte["rotulo"])
        print(f"  {slug:20} acurácia {acuracia_corpus * 100:5.1f}%  AUC {auc_corpus:.3f}")

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, CAMINHO_SAIDA)
    tamanho = CAMINHO_SAIDA.stat().st_size / 1_000_000
    print(
        f"\nModelo salvo em {CAMINHO_SAIDA.relative_to(RAIZ)} "
        f"({tamanho:.1f} MB, classes {list(modelo.classes_)}) "
        f"em {time.monotonic() - inicio:.0f}s"
    )


if __name__ == "__main__":
    main()
