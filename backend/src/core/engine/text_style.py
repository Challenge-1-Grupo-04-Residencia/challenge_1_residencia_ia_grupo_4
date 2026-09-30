"""Heurísticas de estilo de texto usadas pela camada N2 (RF-22, RF-24).

São funções puras sobre a string do texto, separadas da camada para poderem ser
testadas e calibradas sem carregar modelo de ML. Todas devolvem um índice de 0 a 1.
"""

import re

#: Palavras e expressões de urgência típicas de corrente de mensageiro.
_URGENCIA = (
    "urgente",
    "repassem",
    "repasse",
    "compartilhe",
    "compartilhem",
    "acordem",
    "antes que apaguem",
    "a mídia não mostra",
    "a midia nao mostra",
    "não vão te contar",
    "nao vao te contar",
    "última hora",
    "ultima hora",
    "bomba",
    "chocante",
    "você não vai acreditar",
    "voce nao vai acreditar",
)

_PALAVRA = re.compile(r"\b[\wÀ-ÿ]+\b", re.UNICODE)
_URL = re.compile(r"https?://\S+")

#: Órgãos e veículos cuja menção conta como citação verificável mesmo sem link.
_FONTES_NOMEADAS = (
    "ministério",
    "ministerio",
    "ibge",
    "fiocruz",
    "anvisa",
    "oms",
    "organização mundial da saúde",
    "supremo tribunal federal",
    "stf",
    "universidade",
    "segundo o estudo",
    "de acordo com a pesquisa",
    "revista científica",
    "revista cientifica",
)


def indice_sensacionalismo(texto: str) -> float:
    """Quanto o texto grita, de 0 (sóbrio) a 1 (corrente de WhatsApp).

    Combina três marcas independentes: palavras inteiras em caixa alta, pontuação
    repetida e vocabulário de urgência. Cada marca é normalizada e a média das três é
    o índice — assim um texto que só usa muitas exclamações não satura sozinho.
    """
    palavras = _PALAVRA.findall(texto)
    if not palavras:
        return 0.0

    # Caixa alta: só conta palavras de 3+ letras, para não pegar siglas como "STF".
    longas = [p for p in palavras if len(p) >= 3]
    caixa_alta = sum(1 for p in longas if p.isupper()) / len(longas) if longas else 0.0

    # Pontuação repetida ("!!!", "???") normalizada por 100 palavras.
    repetida = len(re.findall(r"[!?]{2,}", texto))
    pontuacao = min(1.0, repetida / max(1, len(palavras) / 100) / 3)

    baixo = texto.lower()
    urgencia = min(1.0, sum(1 for termo in _URGENCIA if termo in baixo) / 3)

    return min(1.0, (caixa_alta + pontuacao + urgencia) / 3)


def indice_citacao_de_fontes(texto: str) -> float:
    """Proporção de citações verificáveis no texto, de 0 a 1.

    Conta links e menções a órgãos nomeados, normalizando por três: um texto com três
    ou mais citações já é considerado bem ancorado.
    """
    baixo = texto.lower()
    links = len(_URL.findall(texto))
    nomeadas = sum(1 for f in _FONTES_NOMEADAS if f in baixo)
    return min(1.0, (links + nomeadas) / 3)
