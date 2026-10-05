#!/usr/bin/env python
"""Roda o pipeline numa bateria de exemplos com resultado esperado (RNF-07).

    uv run python backend/scripts/bateria_de_exemplos.py
    uv run python backend/scripts/bateria_de_exemplos.py --sem-rede

Serve para ver o motor inteiro trabalhando em casos conhecidos, e para conferir depois
de mexer em peso, léxico ou limiar se a Vera continua acertando o que acertava. Usa a
busca de verdade, então é diagnóstico e não teste — a suíte do `pytest` não toca a rede.

## De onde vêm os exemplos

As alegações falsas do primeiro bloco são **reais**: foram colhidas dos títulos das
checagens publicadas pelo G1 Fato ou Fake e pelo Aos Fatos, que é a única forma honesta
de ter rótulo confiável sem inventar. As do segundo bloco são correntes no formato que
circula em mensageiro. As verdadeiras são fatos noticiados por veículos da base curada.

## Como ler o resultado

Erro para o lado de "Inconclusiva" é o erro aceitável: a Vera não cravou, e por RN-12 e
RN-04 é isso que ela deve fazer quando não apurou o bastante. Erro para o lado de dar
veredito trocado — chamar de falsa uma notícia verdadeira, ou confirmar uma fake — é
bug de produto.

Sem o Ollama no ar, S-12 fica sem medição e vale 20 dos 63 pontos mensuráveis: boa parte
dos casos fica logo abaixo do corte de confiança de RN-04 e sai como Inconclusiva. É o
desenho funcionando — a camada caríssima existe para os casos que as baratas não
resolveram —, mas quem quiser ver o motor fechando veredito precisa de
``./scripts/subir.sh --com-ollama``.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.engine.n2_content import CamadaN2Conteudo  # noqa: E402
from src.core.engine.n3_corroboration import CamadaN3Corroboracao  # noqa: E402
from src.core.engine.n4_nli import CamadaN4Inferencia, ErroDoProvedor  # noqa: E402
from src.core.engine.orchestrator import Orquestrador  # noqa: E402
from src.core.entities.claim import NoticiaRequest  # noqa: E402
from src.core.ports.news_search import BuscaIndisponivel  # noqa: E402

CONVERSA, FALSA, VERDADEIRA, INCONCLUSIVA = (
    "conversa",
    "falsa",
    "verdadeira",
    "inconclusiva",
)

#: ``(esperado, texto)``. O esperado é o que a Vera *deveria* dizer.
EXEMPLOS: tuple[tuple[str, str], ...] = (
    # --- Não é checagem: a triagem responde sem rodar o pipeline -------------------
    (CONVERSA, "oi"),
    (CONVERSA, "bom dia, tudo bem?"),
    (CONVERSA, "quem é você?"),
    (CONVERSA, "obrigada, Vera!"),
    # --- Alegações reais desmentidas por agência (RF-17, RN-01) --------------------
    (FALSA, "Lula jogou a bandeira do Brasil no chão após votar"),
    (
        FALSA,
        "André Mendonça alterou locais de votação em uma das comunidades mais "
        "lulistas do Rio",
    ),
    (FALSA, "eleitores puderam votar on-line pelo celular por causa da chuva"),
    (FALSA, "a urna anula o voto se o eleitor aperta confirma quando não deveria"),
    (
        FALSA,
        "a urna eletrônica no Distrito Federal tinha votos registrados antes da "
        "votação começar",
    ),
    (FALSA, "a cola eleitoral distribuída em Camaçari não foi produzida pelo TRE-BA"),
    (FALSA, "Gilmar Mendes entrou na cabine de votação com o celular na mão"),
    (FALSA, "pesquisa mostra Flávio com 61% das intenções de voto"),
    # --- Correntes de mensageiro, no formato que circula ---------------------------
    (
        FALSA,
        "URGENTE!!! REPASSEM ANTES QUE APAGUEM!!! Descobriram que a vacina da covid "
        "tem grafeno e os medicos estao escondendo!!! COMPARTILHEM!!!",
    ),
    (
        FALSA,
        "Esses bandidos corruptos do congresso sao uns vagabundos ladroes, gente "
        "podre e nojenta que aprovou isso de madrugada pra roubar o nosso dinheiro.",
    ),
    (
        FALSA,
        "Um estudo sigiloso revelou que o consumo diario de agua morna com limao em "
        "jejum elimina completamente qualquer celula cancerigena do organismo em "
        "duas semanas.",
    ),
    (
        FALSA,
        "Descoberto que as antenas 5G instaladas nas cidades brasileiras emitem "
        "radiacao que causa cancer e os orgaos de saude sabem disso ha anos.",
    ),
    (
        FALSA,
        "ATENCAO!!! COMPARTILHEM URGENTE!!! O governo vai taxar o Pix em 15% a "
        "partir do mes que vem e ninguem esta falando disso!!! ACORDEM!!!",
    ),
    # --- Fatos noticiados por veículos da base curada -----------------------------
    (
        VERDADEIRA,
        "O Ministerio da Saude confirmou a morte de um paciente por dengue no "
        "interior de Sao Paulo. Segundo a Fiocruz, o risco de novos casos permanece "
        "alto na crise sazonal.",
    ),
    (
        VERDADEIRA,
        "O Supremo Tribunal Federal julgou nesta semana a constitucionalidade do "
        "marco temporal das terras indigenas, segundo informou o proprio tribunal.",
    ),
    (
        VERDADEIRA,
        "A OMS divulgou novo relatorio sobre cobertura vacinal infantil no mundo, "
        "segundo a Organizacao Mundial da Saude, com dados do ano passado.",
    ),
    (
        VERDADEIRA,
        "O Banco Central manteve a taxa Selic na reuniao do Copom desta semana, "
        "segundo o comunicado divulgado pela autoridade monetaria.",
    ),
    (
        VERDADEIRA,
        "O Inep divulgou o calendario do Enem deste ano, segundo o Ministerio da "
        "Educacao, com as datas de inscricao e de aplicacao das provas.",
    ),
    # --- Casos em que admitir que não sabe é o acerto ------------------------------
    (INCONCLUSIVA, "o ministro pediu demissao hoje"),
    (INCONCLUSIVA, "meu vizinho disse que vai chover amanha na rua dele"),
    (
        INCONCLUSIVA,
        "A prefeitura de uma cidade pequena do interior anunciou a reforma de uma "
        "praca no bairro central, conforme divulgado pela assessoria municipal.",
    ),
)


class _BuscaDesligada:
    def buscar(self, texto: str, top_k: int = 5):
        raise BuscaIndisponivel("execução com --sem-rede")


def _provedor_desligado(prompt: str) -> dict:
    raise ErroDoProvedor("Ollama não consultado nesta execução")


def _classificar(veredito) -> str:
    """Traduz o veredito para a mesma linguagem do esperado."""
    if veredito.faixa.value == "Conversa":
        return CONVERSA
    if not veredito.exibe_porcentagem or veredito.veracidade is None:
        return INCONCLUSIVA
    if veredito.veracidade <= 40:
        return FALSA
    if veredito.veracidade >= 61:
        return VERDADEIRA
    return INCONCLUSIVA


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__)
    analisador.add_argument(
        "--sem-rede",
        action="store_true",
        help="não consulta a busca; mostra o motor só com os sinais de conteúdo",
    )
    argumentos = analisador.parse_args()

    if argumentos.sem_rede:
        buscador = _BuscaDesligada()
    else:
        from src.infrastructure.search.google_news import BuscadorGoogleNews

        buscador = BuscadorGoogleNews()

    print(f"{'esperado':13}{'V':>7} {'faixa':27}{'C':>6}{'cob':>6} {'regra':9} resultado")
    print("-" * 104)

    acertos = 0
    cautelosos = 0
    for esperado, texto in EXEMPLOS:
        n2 = CamadaN2Conteudo()
        n2.set_proxima(CamadaN3Corroboracao(buscador)).set_proxima(
            CamadaN4Inferencia(_provedor_desligado)
        )
        noticia = NoticiaRequest(texto=texto)
        veredito = Orquestrador(n2).veredito(noticia)
        resultado = noticia.resultado

        obtido = _classificar(veredito)
        acertou = obtido == esperado
        acertos += acertou
        # Errar para o lado de não cravar é o erro aceitável.
        if not acertou and obtido == INCONCLUSIVA:
            cautelosos += 1

        pontuacao = (
            "  —  " if veredito.veracidade is None else f"{veredito.veracidade:5.1f}"
        )
        marca = "OK" if acertou else f"→ {obtido}"
        print(
            f"{esperado:13}{pontuacao} {veredito.faixa.value:27}"
            f"{veredito.confianca:6.2f}{resultado.cobertura:6.2f} "
            f"{str(veredito.regra_aplicada):9} {marca:15} {texto[:34]}"
        )

    total = len(EXEMPLOS)
    print(f"\n{acertos} de {total} como esperado ({acertos / total * 100:.0f}%)")
    if cautelosos:
        print(
            f"{cautelosos} saíram como Inconclusiva em vez de cravar — é o erro "
            "aceitável (RN-04, RN-12)."
        )
    errados = total - acertos - cautelosos
    if errados:
        print(f"{errados} com veredito TROCADO — estes são bug de produto.")
    return 1 if errados else 0


if __name__ == "__main__":
    raise SystemExit(main())
