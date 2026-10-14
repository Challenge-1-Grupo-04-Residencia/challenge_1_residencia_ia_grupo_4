#!/usr/bin/env python
"""Mede a eficácia dos sinais de conteúdo contra os corpora rotulados (RNF-07).

    uv run python ml/scripts/avaliar_sinais.py

Sai com código 1 se algum sinal piorar além da tolerância em relação à linha de base
registrada em :data:`LINHA_DE_BASE`. É a rede que transforma calibragem em algo
verificável num PR: antes, mexer num peso ou num léxico era mudança invisível, e foi
assim que S-07 e S-08 passaram meses **apontando para o lado errado** (AUC 0,41 e 0,39,
abaixo do acaso) sem ninguém notar.

## Como ler as métricas

Os sinais de conteúdo têm formas diferentes e não se comparam pela mesma régua:

- **S-06** fala sempre, então vale a AUC global.
- **S-07 e S-08** são detectores de alta precisão e recall baixo: ficam calados na
  maior parte dos textos. Para eles o que importa é ``P(falsa | disparou)`` contra a
  taxa base, e não a AUC global — um detector que acerta muito quando fala e cala o
  resto do tempo tem AUC global perto de 0,5 **e é útil**. Medir pela régua errada foi
  o que sustentou a calibragem anterior.
- **S-09** fala sempre e é simétrico, então vale a AUC global.

Quando mexer num léxico ou num limiar: rode, confira que nada regrediu, e **atualize a
linha de base no mesmo commit**, com o número novo. A linha de base é registro histórico,
não meta.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "backend"))

from src.core.engine import emotion, text_style  # noqa: E402
from src.core.engine.n2_content import CamadaN2Conteudo, TETO_DOS_DETECTORES  # noqa: E402

DIRETORIO_DATASETS = RAIZ / "datasets"
CORPORA = ("fake-br", "fakerecogna", "faketrue-br", "fakewhatsapp-br", "faketweet-br")
MAXIMO_POR_CORPUS = 4_000
MINIMO_DE_PALAVRAS = 10
SEMENTE = 7

#: Medido em 05/10/2026 sobre 15.854 textos, após a recalibragem da auditoria.
#: ``auc`` para sinais que falam sempre; ``precisao`` para os detectores silenciosos.
LINHA_DE_BASE: dict[str, dict[str, float]] = {
    # Atenção: estes corpora são o conjunto de **treino** do S-06, então a AUC dele aqui
    # é dentro do domínio e não mede generalização. O número honesto de generalização
    # sai do *leave-one-dataset-out* de ml/scripts/treinar_classificador_n2.py (0,59 a
    # 0,95 por corpus). Esta entrada serve para detectar regressão, não para divulgar
    # desempenho — confundir as duas coisas foi exatamente o erro da versão anterior.
    "S-06": {"auc": 0.99},
    "S-07": {"precisao": 0.69, "dispara": 0.125},
    "S-08": {"precisao": 0.67, "dispara": 0.089},
    "S-09": {"auc": 0.62},
}

#: Quanto uma métrica pode cair antes de a execução falhar. Ruído de amostragem entre
#: execuções fica bem abaixo disso.
TOLERANCIA = 0.03

#: Taxa base de notícia falsa; um detector que não supere isto não informa nada.
_MARGEM_SOBRE_A_BASE = 0.05


def carregar() -> pd.DataFrame:
    partes = []
    for slug in CORPORA:
        caminho = DIRETORIO_DATASETS / slug / "padronizado.parquet"
        if not caminho.exists():
            print(f"  [aviso] {slug} não encontrado — pulando")
            continue
        quadro = pd.read_parquet(caminho)
        quadro = quadro[quadro["rotulo"].isin(["falso", "verdadeiro"])]
        quadro = quadro.dropna(subset=["texto"])
        quadro = quadro[quadro["texto"].str.split().str.len() >= MINIMO_DE_PALAVRAS]
        if len(quadro) > MAXIMO_POR_CORPUS:
            quadro = quadro.sample(MAXIMO_POR_CORPUS, random_state=SEMENTE)
        partes.append(quadro[["texto", "rotulo"]])
    if not partes:
        raise SystemExit("nenhum corpus disponível: rode ml/scripts/baixar_datasets.sh")
    return pd.concat(partes, ignore_index=True)


def _scores_dos_sinais(textos: list[str]) -> dict[str, np.ndarray]:
    """Calcula cada sinal exatamente como a camada N2 o calcula, com ``nan`` para
    indisponível — é o que o motor trata como "não medido" (RN-06)."""
    camada = CamadaN2Conteudo()
    if camada.modelo is None:
        raise SystemExit(
            "classificador da N2 não encontrado: rode "
            "ml/scripts/treinar_classificador_n2.py"
        )

    indice_verdadeiro = list(camada.modelo.classes_).index("verdadeiro")
    s06 = camada.modelo.predict_proba(textos)[:, indice_verdadeiro]

    def desconto(indice):
        return np.nan if indice is None else TETO_DOS_DETECTORES * (1.0 - indice)

    s07 = np.array([desconto(text_style.indice_sensacionalismo(t)) for t in textos])
    s08 = np.array(
        [desconto(emotion.indice_intensidade_emocional(t)[0]) for t in textos]
    )
    s09 = np.array([text_style.indice_citacao_de_fontes(t) for t in textos])
    return {"S-06": s06, "S-07": s07, "S-08": s08, "S-09": s09}


def _avaliar_sempre_presente(nome, scores, verdadeiro) -> tuple[dict, list[str]]:
    auc = roc_auc_score(verdadeiro, scores)
    print(f"  {nome}  AUC={auc:.3f}  (fala em 100% dos textos)")
    falhas = []
    esperado = LINHA_DE_BASE[nome]["auc"]
    if auc < esperado - TOLERANCIA:
        falhas.append(f"{nome}: AUC caiu de {esperado:.3f} para {auc:.3f}")
    if auc < 0.5:
        falhas.append(
            f"{nome}: AUC {auc:.3f} abaixo do acaso — o sinal está invertido"
        )
    return {"auc": round(auc, 3)}, falhas


def _avaliar_detector(nome, scores, verdadeiro) -> tuple[dict, list[str]]:
    falou = ~np.isnan(scores)
    taxa_de_disparo = falou.mean()
    taxa_base = 1 - verdadeiro.mean()
    falhas = []

    if falou.sum() < 50:
        print(f"  {nome}  disparou só {falou.sum()} vezes — amostra insuficiente")
        return {"dispara": round(float(taxa_de_disparo), 3)}, falhas

    precisao = 1 - verdadeiro[falou].mean()
    print(
        f"  {nome}  dispara em {taxa_de_disparo * 100:4.1f}% dos textos | "
        f"P(falsa|disparou)={precisao:.3f} contra base {taxa_base:.3f}"
    )

    esperado = LINHA_DE_BASE[nome]
    if precisao < esperado["precisao"] - TOLERANCIA:
        falhas.append(
            f"{nome}: precisão caiu de {esperado['precisao']:.3f} para {precisao:.3f}"
        )
    if taxa_de_disparo < esperado["dispara"] - TOLERANCIA:
        falhas.append(
            f"{nome}: passou a disparar em {taxa_de_disparo * 100:.1f}% dos textos, "
            f"contra {esperado['dispara'] * 100:.1f}% na linha de base — ficou cego"
        )
    if precisao < taxa_base + _MARGEM_SOBRE_A_BASE:
        falhas.append(
            f"{nome}: precisão {precisao:.3f} não supera a taxa base {taxa_base:.3f} — "
            "o sinal não informa nada"
        )
    return {"precisao": round(float(precisao), 3), "dispara": round(float(taxa_de_disparo), 3)}, falhas


def main() -> None:
    print("Carregando corpora:")
    dados = carregar()
    verdadeiro = (dados["rotulo"] == "verdadeiro").to_numpy()
    print(f"  {len(dados)} textos, {(~verdadeiro).sum()} falsos, {verdadeiro.sum()} verdadeiros")

    scores = _scores_dos_sinais(dados["texto"].tolist())
    print("\n--- sinais de conteúdo ---")
    print(
        "  [nota] a AUC do S-06 abaixo é DENTRO DO DOMÍNIO: estes corpora treinaram o\n"
        "         modelo. Generalização só em treinar_classificador_n2.py."
    )
    medido, falhas = {}, []
    for nome in ("S-06", "S-09"):
        medido[nome], novas = _avaliar_sempre_presente(nome, scores[nome], verdadeiro)
        falhas += novas
    for nome in ("S-07", "S-08"):
        medido[nome], novas = _avaliar_detector(nome, scores[nome], verdadeiro)
        falhas += novas

    print("\n--- combinação da N2, como o motor calcula ---")
    pesos = {"S-06": 10.0, "S-07": 5.0, "S-08": 5.0, "S-09": 3.0}
    matriz = np.vstack([scores[nome] for nome in pesos])
    vetor_pesos = np.array(list(pesos.values()))[:, None]
    disponivel = ~np.isnan(matriz)
    peso_observado = (vetor_pesos * disponivel).sum(axis=0)
    soma = np.nansum(vetor_pesos * np.nan_to_num(matriz) * disponivel, axis=0)
    veracidade = np.where(peso_observado > 0, 100 * soma / np.maximum(peso_observado, 1e-9), np.nan)
    tem_score = ~np.isnan(veracidade)
    print(f"  AUC do V só com a N2: {roc_auc_score(verdadeiro[tem_score], veracidade[tem_score]):.3f}")
    falsas = veracidade[tem_score & ~verdadeiro]
    verdadeiras = veracidade[tem_score & verdadeiro]
    print(f"  falsas na faixa <=40:      {(falsas <= 40).mean() * 100:5.1f}%")
    print(f"  verdadeiras na faixa >=60: {(verdadeiras >= 60).mean() * 100:5.1f}%")

    print("\n--- linha de base ---")
    if falhas:
        for falha in falhas:
            print(f"  REGREDIU  {falha}")
        print("\nSe a mudança foi intencional, atualize LINHA_DE_BASE no mesmo commit.")
        raise SystemExit(1)
    print("  nenhuma regressão")
    print(f"  medido agora: {medido}")


if __name__ == "__main__":
    main()
