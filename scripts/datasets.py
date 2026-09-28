#!/usr/bin/env python3
"""Baixa, padroniza e documenta os datasets em PT-BR usados na fase Investigate.

Cada dataset vira uma pasta com o mesmo esquema:

    datasets/<slug>/
        dados/               arquivos originais, como vieram da fonte
        padronizado.parquet  mesmas colunas em todos os datasets
        metadata.json        ficha legível por código
        README.md            o que é, de onde veio, licença e uso previsto
        dicionario.md        colunas, tipos e exemplos dos arquivos originais

Como a padronização é igual em todos, importar tudo é uma linha:

    import pandas as pd, glob
    df = pd.concat(map(pd.read_parquet, glob.glob("datasets/*/padronizado.parquet")))

Uso:
    ./scripts/baixar_datasets.sh              # baixa o que falta, padroniza e documenta
    ./scripts/baixar_datasets.sh --docs       # só refaz padronização e documentação
    ./scripts/baixar_datasets.sh --so fake-br faketrue-br
    ./scripts/baixar_datasets.sh --completo   # inclui downloads pesados e opcionais
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "datasets"

# Esquema padrão: toda base normalizada tem exatamente estas colunas, nesta ordem.
ESQUEMA = [
    "id",               # <slug>:<n>, único entre todos os datasets
    "dataset",          # slug de origem
    "canal",            # noticia | rede_social | whatsapp | checagem | sintetico
    "titulo",           # título, quando existir
    "texto",            # corpo do conteúdo
    "rotulo",           # falso | verdadeiro | outro
    "rotulo_original",  # rótulo como veio da fonte, sem tradução
    "data",             # data de publicação (AAAA-MM-DD), quando existir
    "veiculo",          # veículo ou fonte declarada
    "url",              # link de origem
]

FALSO = ("fake", "falso", "boato", "false", "0")
VERDADEIRO = ("true", "verdadeiro", "verdade", "1")


def normalizar_rotulo(valor) -> str:
    """Traduz o rótulo da fonte para falso / verdadeiro / outro."""
    if valor is None:
        return "outro"
    t = str(valor).strip().strip("[]'\" ").lower()
    if t in FALSO or t.startswith(("fake", "falso", "boato")):
        return "falso"
    if t in VERDADEIRO or t.startswith(("true", "verdadeiro")):
        return "verdadeiro"
    return "outro"


# ---------------------------------------------------------------- manifesto

DATASETS = [
    {
        "slug": "fake-br",
        "nome": "Fake.Br Corpus",
        "antigo": "Fake.br-Corpus",
        "canal": "noticia",
        "git": "roneysco/Fake.br-Corpus",
        "fonte": "https://github.com/roneysco/Fake.br-Corpus",
        "licenca": "Acadêmica — citar o artigo (PROPOR 2018)",
        "periodo": "2016 a 2018",
        "rotulos": "fake e true, balanceado",
        "resumo": (
            "Corpus de referência para fake news em português. Cada notícia falsa tem uma "
            "verdadeira pareada pelo mesmo tema, o que reduz o risco de o modelo aprender o "
            "assunto em vez do estilo."
        ),
        "uso": (
            "Treino e teste da camada **N2 · Conteúdo** (RF-21 a RF-23) e base do conjunto de "
            "avaliação exigido pelo RNF-06."
        ),
        "atencao": (
            "É de 2018: o vocabulário é o das eleições daquele ano. Não usar sozinho para "
            "medir desempenho em notícias atuais."
        ),
    },
    {
        "slug": "fakerecogna",
        "nome": "FakeRecogna",
        "antigo": "FakeRecogna",
        "canal": "noticia",
        "url": [(
            "https://huggingface.co/datasets/recogna-nlp/FakeRecogna/resolve/main/FakeRecogna.csv",
            "FakeRecogna.csv",
        )],
        "fonte": "https://huggingface.co/datasets/recogna-nlp/FakeRecogna",
        "licenca": "MIT",
        "periodo": "até 2021",
        "rotulos": "Classe 0 (falsa) e 1 (verdadeira), balanceado",
        "resumo": (
            "Corpus balanceado com metadados ricos: categoria temática, data, autor e URL de "
            "origem. As falsas vêm de agências de checagem (Boatos, e-Farsas, AFP Checamos) e "
            "as verdadeiras de portais (UOL, G1)."
        ),
        "uso": (
            "Avaliação por tema: mede se a Vera acerta igual em política, saúde e economia, "
            "que é o risco R-07 do mapa de riscos."
        ),
        "atencao": (
            "A direção do rótulo não é óbvia: Classe 0 é falsa e Classe 1 é verdadeira, o "
            "contrário do que a intuição sugere."
        ),
    },
    {
        "slug": "faketrue-br",
        "nome": "FakeTrue.Br",
        "antigo": "FakeTrue.Br",
        "canal": "noticia",
        "git": "jpchav98/FakeTrue.Br",
        "fonte": "https://github.com/jpchav98/FakeTrue.Br",
        "licenca": "Acadêmica — citar o artigo (ERBD 2023)",
        "periodo": "coleta até 2022",
        "rotulos": "pares falsa/verdadeira alinhados",
        "resumo": (
            "Cada linha traz a notícia falsa e a verdadeira correspondente, com os dois links. "
            "As falsas vêm do Boatos.org; as verdadeiras, de G1 e Folha."
        ),
        "uso": (
            "Camada **N3 · Corroboração** (RF-27 e RF-28): é o par pronto entre o boato e a "
            "notícia que o desmente."
        ),
        "atencao": (
            "Na padronização cada par vira duas linhas. A mesma verdadeira aparece em mais de "
            "um par: deduplicar antes de treinar."
        ),
    },
    {
        "slug": "fktc",
        "nome": "FKTC — Fact-checked News",
        "antigo": "FKTC",
        "canal": "noticia",
        "git": "GoloMarcos/FKTC",
        "zip": (
            "https://zenodo.org/records/5236636/files/News.zip?download=1",
            "News.zip",
        ),
        "fonte": "https://github.com/GoloMarcos/FKTC",
        "licenca": "Acadêmica",
        "periodo": "agosto/2018 a maio/2019",
        "rotulos": "1.124 reais e 1.044 falsas no recorte fcn",
        "resumo": (
            "Biblioteca com quatro coleções; a de interesse é a **fcn** (Fact-checked News), "
            "com notícias políticas checadas por Aos Fatos, Lupa e UOL Confere."
        ),
        "uso": "Recorte político para testar o comportamento da Vera em período eleitoral.",
        "atencao": (
            "O repositório não traz os dados: eles vêm de um zip de 460 MB no Zenodo que "
            "inclui coleções em inglês. Por isso só baixa com `--completo`."
        ),
    },
    {
        "slug": "fakegen-br",
        "nome": "FakeGen.BR (Expanded Fake News Corpus)",
        "antigo": "expanded_fake_news_corpus",
        "canal": "sintetico",
        "git": "Pedrest15/expanded_fake_news_corpus",
        "fonte": "https://github.com/Pedrest15/expanded_fake_news_corpus",
        "licenca": "Verificar no repositório",
        "periodo": "gerado em 2026",
        "rotulos": "pares gerados a partir de notícias do Fake.Br",
        "resumo": (
            "Não é um corpus coletado: são **20 itens gerados por LLM** (GPT-4.1-mini) a "
            "partir de notícias do Fake.Br, como réplica de um experimento."
        ),
        "uso": (
            "Referência para a Guiding Question sobre IA generativa aumentar o realismo da "
            "desinformação, e material de teste para o RF-25 (texto gerado por IA)."
        ),
        "atencao": (
            "Tamanho pequeno e origem sintética: **não usar em treino nem em avaliação** de "
            "desempenho geral."
        ),
    },
    {
        "slug": "fakenewsbr-v6",
        "nome": "FakenewsBR v6",
        "antigo": "fakenewsbr-v4",
        "canal": "noticia",
        "git": "thiago-cg/fakenewsbr-v4",
        "url": [(
            "https://media.githubusercontent.com/media/thiago-cg/fakenewsbr-v4/main/data/"
            f"{f}", f,
        ) for f in ("FakenewsBR_v6_public.csv", "FakenewsBR_v6_labels.csv")],
        "fonte": "https://github.com/thiago-cg/fakenewsbr-v4",
        "licenca": "Verificar no repositório",
        "periodo": "2021 a 2026",
        "rotulos": "230.900 true e 66.772 fake",
        "resumo": (
            "A maior base do levantamento. Reúne alegações, mensagens virais, checagens de "
            "agências e manchetes legítimas de portais brasileiros e portugueses, com marcas "
            "de estilo já calculadas: exclamações, interrogações, reticências e proporção de "
            "caixa alta."
        ),
        "uso": (
            "Responde à pergunta 'o que no texto entrega que algo é falso' sem precisar "
            "calcular nada (RF-22). A coluna de data permite estudar a janela entre a "
            "circulação e o desmentido."
        ),
        "atencao": (
            "Contém 7.160 registros do próprio Fake.Br: treinar aqui e avaliar lá infla a "
            "métrica. Além disso há 3,5 verdadeiras para cada falsa."
        ),
    },
    {
        "slug": "fakewhatsapp-br",
        "nome": "FakeWhatsApp.Br",
        "antigo": "FakeWhatsApp.Br",
        "canal": "whatsapp",
        "git": "cabrau/FakeWhatsApp.Br",
        "fonte": "https://github.com/cabrau/FakeWhatsApp.Br",
        "licenca": "Ver LICENSE no repositório",
        "periodo": "2018 e 2020",
        "rotulos": "misinformation 0/1 no recorte rotulado",
        "resumo": (
            "Mensagens de grupos públicos de WhatsApp, anonimizadas, com data, hora, grupo e "
            "estado, contagem de compartilhamentos e um grafo de propagação (`edges.p`)."
        ),
        "uso": (
            "É a única base do levantamento que mostra a difusão real: quando a mensagem "
            "aparece, quantas vezes é reencaminhada e por quais grupos passa."
        ),
        "atencao": (
            "Dados pessoais, ainda que anonimizados: tratar conforme o RNF-11 e não "
            "republicar mensagens brutas."
        ),
    },
    {
        "slug": "faketweet-br",
        "nome": "FakeTweet.Br",
        "antigo": "FakeTweet.Br",
        "canal": "rede_social",
        "git": "prc992/FakeTweet.Br",
        "fonte": "https://github.com/prc992/FakeTweet.Br",
        "licenca": "Acadêmica",
        "periodo": "2018",
        "rotulos": "188 fake e 91 true",
        "resumo": "Corpus pequeno do Twitter, com retweets, favoritos e data de cada publicação.",
        "uso": "Sinal de engajamento: relaciona alcance com veracidade.",
        "atencao": "Poucas centenas de registros: serve para exploração, não para treino.",
    },
    {
        "slug": "central-de-fatos",
        "nome": "Central de Fatos",
        "antigo": "central_de_fatos",
        "canal": "checagem",
        "url": [(
            "https://huggingface.co/datasets/fake-news-UFG/central_de_fatos/resolve/main/"
            "central_de_fatos.tsv", "central_de_fatos.tsv",
        )],
        "fonte": "https://huggingface.co/datasets/fake-news-UFG/central_de_fatos",
        "licenca": "Ver o card do dataset",
        "periodo": "2013 a 2021",
        "rotulos": "veredito da agência, em texto livre",
        "resumo": (
            "Checagens de seis agências reunidas: Boatos (5.523), Lupa (2.574), Aos Fatos "
            "(1.679), Fato ou Fake (917), Estadão Verifica (593) e Comprova (361)."
        ),
        "uso": (
            "Base para a camada **N1 · Fonte**: alimenta a regra RN-01 e o histórico de "
            "falsas por domínio (RF-18)."
        ),
        "atencao": (
            "O veredito é texto livre e varia por agência ('boato', 'FALSO', 'Enganoso', "
            "'FORA DE CONTEXTO'). O que não for claramente falso ou verdadeiro vira `outro` "
            "na padronização, e o valor original fica em `rotulo_original`."
        ),
    },
    {
        "slug": "factck-br",
        "nome": "FACTCK.BR",
        "antigo": "FACTCK.BR",
        "canal": "checagem",
        "url": [(
            "https://raw.githubusercontent.com/jghm-f/FACTCK.BR/master/FACTCKBR.tsv",
            "FACTCKBR.tsv",
        )],
        "fonte": "https://github.com/jghm-f/FACTCK.BR",
        "licenca": "Acadêmica",
        "periodo": "2018 e 2019",
        "rotulos": "escala fina: Falso, Exagerado, Distorcido, Sem contexto, Verdadeiro",
        "resumo": (
            "Alegações no padrão **ClaimReview**, o mesmo formato devolvido pela Google Fact "
            "Check Tools API."
        ),
        "uso": (
            "Referência de como estruturar o resultado da Vera e de que escala de veredito as "
            "agências usam na prática."
        ),
        "atencao": "Os rótulos vêm com e sem maiúscula ('Falso' e 'falso'): normalizar antes de contar.",
    },
    {
        "slug": "portuguese-fact-checking",
        "nome": "MuMiN-PT e COVID19.BR",
        "antigo": "portuguese-fact-checking",
        "canal": "rede_social",
        "url": [(
            "https://huggingface.co/datasets/ju-resplande/portuguese-fact-checking/resolve/"
            f"main/{f}", f,
        ) for f in (
            "MuMiN-PT.parquet", "MuMiN-PT_raw.parquet",
            "COVID19.BR.parquet", "COVID19.BR_raw.parquet", "Fake.br.parquet",
        )],
        "fonte": "https://huggingface.co/datasets/ju-resplande/portuguese-fact-checking",
        "licenca": "Ver o card do dataset",
        "periodo": "2020 a 2022",
        "rotulos": "fake e true por publicação",
        "resumo": (
            "Publicações de rede social ligadas à alegação checada, com quase-duplicatas, "
            "resultados de busca e de checagem para cada uma."
        ),
        "uso": (
            "Mostra a mesma alegação reaparecendo reescrita, que é o caso que o RF-11 "
            "(reaproveitar checagens) e o RF-27 precisam resolver."
        ),
        "atencao": (
            "Muito desbalanceado (1.343 fake para 61 true no MuMiN-PT) e o arquivo "
            "`Fake.br.parquet` repete o Fake.Br, que já tem pasta própria: fica fora da "
            "padronização para não duplicar."
        ),
    },
]

POR_SLUG = {d["slug"]: d for d in DATASETS}


# ---------------------------------------------------------------- download


def achar(dados: Path, nome: str) -> Path | None:
    """Maior arquivo com este nome dentro de dados/ (evita pegar ponteiro de Git LFS)."""
    achados = [p for p in dados.rglob(nome) if p.is_file()]
    return max(achados, key=lambda p: p.stat().st_size) if achados else None


GERADOS = {"dados", "README.md", "dicionario.md", "metadata.json", "padronizado.parquet"}


def baixar(ds: dict, completo: bool) -> None:
    pasta = DESTINO / ds["slug"]
    dados = pasta / "dados"
    dados.mkdir(parents=True, exist_ok=True)

    # Organização antiga: arquivos soltos na pasta do dataset ou em pasta de outro nome.
    # Em disco que não diferencia maiúsculas, a pasta antiga pode ser a mesma que a nova.
    origens = [pasta]
    antigo = DESTINO / ds.get("antigo", "")
    if ds.get("antigo") and antigo.is_dir() and not antigo.samefile(pasta):
        origens.append(antigo)
    for origem in origens:
        for item in list(origem.iterdir()):
            if item.name in GERADOS or item == dados:
                continue
            alvo = dados / item.name
            print(f"  migrando {item.name} -> dados/")
            if alvo.exists():
                continue
            item.rename(alvo)
        if origem != pasta and not any(origem.iterdir()):
            origem.rmdir()

    # Clone só quando dados/ está vazia; o conteúdo do repositório fica na raiz de dados/.
    if "git" in ds and not any(dados.iterdir()):
        print(f"  clonando {ds['git']}...")
        temp = pasta / "_tmp_clone"
        tentativas = 3
        for tentativa in range(1, tentativas + 1):
            if temp.exists():
                shutil.rmtree(temp, ignore_errors=True)
            cmd = [
                "git",
                "-c", "http.version=HTTP/1.1",
                "-c", "http.postBuffer=1048576000",
                "clone", "--depth", "1",
                f"https://github.com/{ds['git']}.git", str(temp),
            ]
            try:
                subprocess.run(cmd, check=True)
                for item in list(temp.iterdir()):
                    shutil.move(str(item), str(dados / item.name))
                shutil.rmtree(temp, ignore_errors=True)
                break
            except Exception as e:
                if temp.exists():
                    shutil.rmtree(temp, ignore_errors=True)
                if tentativa == tentativas:
                    raise
                print(f"  tentativa {tentativa} falhou ({e}), tentando novamente...")
                time.sleep(2)

    for url, nome in ds.get("url", []):
        existente = achar(dados, nome)
        if existente and existente.stat().st_size > 1024:
            print(f"  já existe: {nome}")
            continue
        print(f"  baixando {nome}...")
        subprocess.run(["curl", "-sL", "--retry", "3", "-o", str(dados / nome), url], check=True)

    if "zip" in ds:
        url, nome = ds["zip"]
        alvo = dados / nome
        marca = dados / "News"
        if marca.exists():
            print(f"  já extraído: {marca.name}/")
        elif not completo:
            print(f"  pulando {nome} (download pesado; use --completo)")
        else:
            print(f"  baixando {nome} (pode demorar)...")
            subprocess.run(["curl", "-sL", "--retry", "3", "-o", str(alvo), url], check=True)
            try:
                with zipfile.ZipFile(alvo) as z:
                    z.extractall(dados)
                alvo.unlink()
                print("  extraído")
            except zipfile.BadZipFile:
                print("  ERRO: download incompleto; rode de novo com --completo")
                alvo.unlink(missing_ok=True)


# ---------------------------------------------------------------- padronização


def _linhas(slug: str, registros: list[dict]):
    import pandas as pd

    df = pd.DataFrame(registros, columns=ESQUEMA[1:])
    df.insert(0, "id", [f"{slug}:{i}" for i in range(len(df))])
    df["texto"] = df["texto"].astype("string").str.strip()
    return df[df["texto"].notna() & (df["texto"] != "")].reset_index(drop=True)


def _reg(ds, texto, rotulo_original, titulo=None, data=None, veiculo=None, url=None) -> dict:
    return {
        "dataset": ds["slug"],
        "canal": ds["canal"],
        "titulo": titulo,
        "texto": texto,
        "rotulo": normalizar_rotulo(rotulo_original),
        "rotulo_original": None if rotulo_original is None else str(rotulo_original),
        "data": data,
        "veiculo": veiculo,
        "url": url,
    }


def _dominio(url) -> str | None:
    u = str(url or "")
    return u.split("/")[2] if u.startswith("http") and len(u.split("/")) > 2 else None


def padronizar(ds: dict):
    import pandas as pd

    dados = DESTINO / ds["slug"] / "dados"
    slug = ds["slug"]
    regs: list[dict] = []

    if slug == "fake-br":
        base = next((p for p in dados.rglob("full_texts") if p.is_dir()), None)
        for rotulo in ("fake", "true"):
            for arq in sorted((base / rotulo).glob("*.txt")) if base else []:
                texto = arq.read_text(encoding="utf-8", errors="ignore")
                titulo = texto.split("\n", 1)[0].strip()
                regs.append(_reg(ds, texto, rotulo, titulo=titulo))

    elif slug == "fakerecogna":
        df = pd.read_csv(achar(dados, "FakeRecogna.csv"))
        for _, r in df.iterrows():
            # Classe 0 = falsa, Classe 1 = verdadeira (a coluna vem como número)
            try:
                classe = float(r["Classe"])
            except (TypeError, ValueError):
                continue
            original = "fake" if classe == 0 else "true"
            regs.append(_reg(ds, r["Noticia"], original, titulo=r["Titulo"],
                             data=r["Data"], veiculo=_dominio(r["URL"]), url=r["URL"]))

    elif slug == "faketrue-br":
        df = pd.read_csv(achar(dados, "FakeTrueBr_corpus.csv"))
        for _, r in df.iterrows():
            regs.append(_reg(ds, r["fake"], "fake", titulo=r.get("title_fake"),
                             veiculo=_dominio(r.get("link_f")), url=r.get("link_f")))
            regs.append(_reg(ds, r["true"], "true",
                             veiculo=_dominio(r.get("link_t")), url=r.get("link_t")))

    elif slug == "fktc":
        arq = achar(dados, "fcn.plk")
        if arq:
            df = pd.read_pickle(arq)
            col_texto = next((c for c in ("text", "texto", "news", "content") if c in df.columns), None)
            col_rot = next((c for c in ("class", "label", "classe") if c in df.columns), None)
            for _, r in df.iterrows():
                regs.append(_reg(ds, r[col_texto], r[col_rot] if col_rot else None))

    elif slug == "fakegen-br":
        arq = achar(dados, "data.json")
        itens = json.loads(arq.read_text(encoding="utf-8")).get("items", []) if arq else []
        for it in itens:
            if it.get("fake_text"):
                regs.append(_reg(ds, it["fake_text"], "fake", titulo=it.get("fake_headline"),
                                 veiculo=it.get("source")))
            if it.get("true_text"):
                regs.append(_reg(ds, it["true_text"], "true", titulo=it.get("true_headline"),
                                 veiculo=it.get("source")))

    elif slug == "fakenewsbr-v6":
        arq = achar(dados, "FakenewsBR_v6_public.csv")
        if arq:
            colunas = ["text_clean", "text", "label", "date_iso", "source_description",
                       "url_review", "factcheck_url"]
            for pedaco in pd.read_csv(arq, usecols=lambda c: c in colunas, chunksize=50_000):
                for _, r in pedaco.iterrows():
                    regs.append(_reg(ds, r.get("text_clean") or r.get("text"), r.get("label"),
                                     data=r.get("date_iso"), veiculo=r.get("source_description"),
                                     url=r.get("url_review") or r.get("factcheck_url")))

    elif slug == "fakewhatsapp-br":
        c2018 = achar(dados, "fakeWhatsApp.BR_2018_content_only.csv")
        if c2018:
            df = pd.read_csv(c2018)
            for _, r in df.iterrows():
                regs.append(_reg(ds, r["text"], "fake" if r["misinformation"] == 1 else "true",
                                 data=r.get("date")))
        c2020 = achar(dados, "wpp_2020.csv")
        if c2020:
            df = pd.read_csv(c2020)
            for _, r in df.iterrows():
                regs.append(_reg(ds, r["text"], "fake" if r["misinformation"] == 1 else "true",
                                 veiculo=r.get("source")))

    elif slug == "faketweet-br":
        arq = achar(dados, "FakeTweetBr.csv")
        if arq:
            df = pd.read_csv(arq)
            for _, r in df.iterrows():
                regs.append(_reg(ds, r["text"], r["classificacao"], titulo=r.get("subject"),
                                 data=r.get("date"), veiculo="twitter", url=r.get("permalink")))

    elif slug == "central-de-fatos":
        df = pd.read_csv(achar(dados, "central_de_fatos.tsv"), sep="\t", on_bad_lines="skip")
        for _, r in df.iterrows():
            regs.append(_reg(ds, r.get("text_news"), r.get("rating"), titulo=r.get("title"),
                             data=str(r.get("publication_date"))[:10],
                             veiculo=r.get("source_name"), url=r.get("url")))

    elif slug == "factck-br":
        df = pd.read_csv(achar(dados, "FACTCKBR.tsv"), sep="\t", on_bad_lines="skip")
        for _, r in df.iterrows():
            regs.append(_reg(ds, r.get("claimReviewed"), r.get("alternativeName"),
                             titulo=r.get("title"), data=str(r.get("datePublished"))[:10],
                             veiculo=_dominio(r.get("URL")), url=r.get("URL")))

    elif slug == "portuguese-fact-checking":
        for nome in ("MuMiN-PT.parquet", "COVID19.BR.parquet"):
            arq = achar(dados, nome)
            if not arq:
                continue
            df = pd.read_parquet(arq, columns=["text_no_url", "label"])
            for _, r in df.iterrows():
                regs.append(_reg(ds, r["text_no_url"], r["label"],
                                 veiculo=nome.replace(".parquet", "")))

    return _linhas(slug, regs)


# ---------------------------------------------------------------- documentação

EXTENSOES = {".csv", ".tsv", ".parquet", ".plk", ".pkl"}
IGNORAR = {".git", "__pycache__", "node_modules"}


def tamanho_legivel(n: float) -> str:
    for unidade in ("B", "KB", "MB", "GB"):
        if n < 1024 or unidade == "GB":
            return f"{n:.0f} {unidade}" if unidade == "B" else f"{n:.1f} {unidade}"
        n /= 1024
    return f"{n:.1f} GB"


def arquivos_de_dados(dados: Path) -> list[Path]:
    achados = [
        p for p in dados.rglob("*")
        if p.suffix.lower() in EXTENSOES and p.is_file()
        and not any(parte in IGNORAR for parte in p.parts) and p.stat().st_size > 512
    ]
    return sorted(achados, key=lambda p: -p.stat().st_size)[:6]


def ler_amostra(caminho: Path):
    import pandas as pd

    if caminho.suffix.lower() == ".parquet":
        df = pd.read_parquet(caminho)
        return df.head(3000), len(df)
    if caminho.suffix.lower() in (".plk", ".pkl"):
        df = pd.read_pickle(caminho)
        return df.head(3000), len(df)
    sep = "\t" if caminho.suffix.lower() == ".tsv" else ","
    amostra = pd.read_csv(caminho, sep=sep, nrows=3000, on_bad_lines="skip")
    linhas = sum(
        len(p) for p in pd.read_csv(caminho, sep=sep, chunksize=100_000,
                                    on_bad_lines="skip", usecols=[0])
    )
    return amostra, linhas


def exemplo(valor) -> str:
    texto = str(valor).replace("|", "\\|").replace("\n", " ").strip()
    return (texto[:60] + "…") if len(texto) > 60 else (texto or "—")


def dicionario(ds: dict, padrao) -> str:
    dados = DESTINO / ds["slug"] / "dados"
    linhas = [
        f"# Dicionário de dados — {ds['nome']}",
        "",
        "> Arquivo gerado por `scripts/datasets.py` a partir dos arquivos reais.",
        "> Para atualizar: `./scripts/baixar_datasets.sh --docs`.",
        "",
        "## `padronizado.parquet`",
        "",
        f"**{len(padrao):,} linhas** no esquema comum a todos os datasets.".replace(",", "."),
        "",
        "| Coluna | Tipo | Descrição |",
        "| --- | --- | --- |",
        "| `id` | texto | `<slug>:<n>`, único entre todos os datasets |",
        "| `dataset` | texto | slug de origem |",
        "| `canal` | texto | noticia, rede_social, whatsapp, checagem ou sintetico |",
        "| `titulo` | texto | título, quando a fonte tem |",
        "| `texto` | texto | corpo do conteúdo |",
        "| `rotulo` | texto | falso, verdadeiro ou outro |",
        "| `rotulo_original` | texto | rótulo como veio da fonte |",
        "| `data` | texto | data de publicação, quando existir |",
        "| `veiculo` | texto | veículo ou fonte declarada |",
        "| `url` | texto | link de origem |",
        "",
    ]
    if len(padrao):
        contagem = padrao["rotulo"].value_counts()
        linhas += ["**Distribuição de `rotulo`**", "", "| Valor | Linhas |", "| --- | ---: |"]
        linhas += [f"| {v} | {n:,} |".replace(",", ".") for v, n in contagem.items()]
        linhas.append("")

    linhas += ["## Arquivos originais", ""]
    arquivos = arquivos_de_dados(dados)
    if not arquivos:
        linhas += ["Nenhum arquivo tabular em `dados/`. Rode o download primeiro.", ""]
        return "\n".join(linhas)

    for caminho in arquivos:
        rel = caminho.relative_to(dados)
        try:
            amostra, total = ler_amostra(caminho)
        except Exception as erro:
            linhas += [f"### `{rel}`", "", f"Não foi possível ler: {erro}", ""]
            continue
        linhas += [
            f"### `{rel}`",
            "",
            f"**{total:,} linhas** · {len(amostra.columns)} colunas · "
            f"{tamanho_legivel(caminho.stat().st_size)}".replace(",", "."),
            "",
            "| Coluna | Tipo | Preenchido | Valores distintos | Exemplo |",
            "| --- | --- | ---: | ---: | --- |",
        ]
        for coluna in amostra.columns:
            serie = amostra[coluna]
            try:  # colunas com listas dentro não são contáveis
                distintos = serie.nunique(dropna=True)
                distintos_txt = str(distintos) if distintos < len(serie) else "todos"
            except TypeError:
                distintos_txt = "—"
            primeiro = serie.dropna()
            linhas.append(
                f"| `{coluna}` | {serie.dtype} | {serie.notna().mean() * 100:.0f}% | "
                f"{distintos_txt} | "
                f"{exemplo(primeiro.iloc[0]) if len(primeiro) else '—'} |"
            )
        linhas.append("")
    return "\n".join(linhas)


def readme(ds: dict, padrao) -> str:
    dados = DESTINO / ds["slug"] / "dados"
    total = sum(p.stat().st_size for p in dados.rglob("*") if p.is_file()) if dados.exists() else 0
    contagem = padrao["rotulo"].value_counts().to_dict() if len(padrao) else {}
    distrib = " · ".join(f"{k}: {v:,}".replace(",", ".") for k, v in contagem.items()) or "—"
    return "\n".join([
        f"# {ds['nome']}",
        "",
        ds["resumo"],
        "",
        "| | |",
        "| --- | --- |",
        f"| **Fonte** | {ds['fonte']} |",
        f"| **Licença** | {ds['licenca']} |",
        f"| **Período** | {ds['periodo']} |",
        f"| **Rótulos na origem** | {ds['rotulos']} |",
        f"| **Linhas padronizadas** | {len(padrao):,} |".replace(",", "."),
        f"| **Distribuição** | {distrib} |",
        f"| **Canal** | {ds['canal']} |",
        f"| **Tamanho em disco** | {tamanho_legivel(total)} |",
        "",
        "## Para que serve no projeto",
        "",
        ds["uso"],
        "",
        "## Atenção",
        "",
        ds["atencao"],
        "",
        "## Como importar",
        "",
        "```python",
        "import pandas as pd",
        f'df = pd.read_parquet("datasets/{ds["slug"]}/padronizado.parquet")',
        "```",
        "",
        "As colunas são as mesmas em todos os datasets; veja [dicionario.md](dicionario.md).",
        "",
    ])


def leia_me_geral(resumos: list[dict]) -> str:
    linhas = [
        "# Datasets padronizados",
        "",
        "Pasta gerada por `scripts/datasets.py`. **Nada aqui vai para o Git.**",
        "",
        "Todo dataset segue o mesmo esquema, então importar tudo é uma linha:",
        "",
        "```python",
        "import pandas as pd, glob",
        'df = pd.concat(map(pd.read_parquet, glob.glob("datasets/*/padronizado.parquet")))',
        "```",
        "",
        "| Dataset | Slug | Canal | Linhas | falso | verdadeiro | outro |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for r in resumos:
        linhas.append(
            f"| {r['nome']} | `{r['slug']}` | {r['canal']} | {r['linhas']:,} | "
            f"{r['falso']:,} | {r['verdadeiro']:,} | {r['outro']:,} |".replace(",", ".")
        )
    total = sum(r["linhas"] for r in resumos)
    linhas += [
        "",
        f"**Total: {total:,} linhas padronizadas.**".replace(",", "."),
        "",
        "Cada pasta tem `dados/` (original), `padronizado.parquet`, `metadata.json`, "
        "`README.md` e `dicionario.md`.",
        "",
    ]
    return "\n".join(linhas)


# ---------------------------------------------------------------- principal


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--docs", action="store_true", help="só refaz padronização e documentação")
    ap.add_argument("--so", "--só", dest="so", nargs="+", help="processa apenas estes slugs")
    ap.add_argument("--completo", action="store_true", help="inclui downloads pesados")
    args = ap.parse_args()

    escolhidos = [d for d in DATASETS if not args.so or d["slug"] in args.so]
    if not escolhidos:
        print("slugs disponíveis:", ", ".join(POR_SLUG))
        return 1

    resumos = []
    for ds in escolhidos:
        print(f"\n{ds['nome']} ({ds['slug']})")
        if not args.docs:
            baixar(ds, args.completo)

        pasta = DESTINO / ds["slug"]
        pasta.mkdir(parents=True, exist_ok=True)
        try:
            padrao = padronizar(ds)
        except Exception as erro:
            print(f"  aviso: não foi possível padronizar ({erro})")
            padrao = _linhas(ds["slug"], [])
        padrao.to_parquet(pasta / "padronizado.parquet", index=False)
        print(f"  padronizado.parquet: {len(padrao)} linhas")

        contagem = padrao["rotulo"].value_counts().to_dict() if len(padrao) else {}
        ficha = {k: ds[k] for k in
                 ("slug", "nome", "canal", "fonte", "licenca", "periodo", "rotulos")}
        ficha |= {
            "linhas": int(len(padrao)),
            "distribuicao": {k: int(v) for k, v in contagem.items()},
            "esquema": ESQUEMA,
            "arquivo": "padronizado.parquet",
        }
        (pasta / "metadata.json").write_text(
            json.dumps(ficha, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (pasta / "README.md").write_text(readme(ds, padrao), encoding="utf-8")
        (pasta / "dicionario.md").write_text(dicionario(ds, padrao), encoding="utf-8")
        print("  metadata.json, README.md e dicionario.md atualizados")

        resumos.append({
            "slug": ds["slug"], "nome": ds["nome"], "canal": ds["canal"],
            "linhas": int(len(padrao)),
            "falso": int(contagem.get("falso", 0)),
            "verdadeiro": int(contagem.get("verdadeiro", 0)),
            "outro": int(contagem.get("outro", 0)),
        })

    if not args.so:
        (DESTINO / "LEIA-ME.md").write_text(leia_me_geral(resumos), encoding="utf-8")
        (DESTINO / "indice.json").write_text(
            json.dumps({"esquema": ESQUEMA, "datasets": resumos}, ensure_ascii=False, indent=2)
            + "\n", encoding="utf-8")
        print("\nindice.json e LEIA-ME.md atualizados")

    print(f"\npronto: {len(escolhidos)} datasets em {DESTINO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
