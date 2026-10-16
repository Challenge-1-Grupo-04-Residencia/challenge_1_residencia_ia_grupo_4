"""Base curada de veículos brasileiros (RF-14, RF-15).

Lista de partida para que S-01 e S-11 possam ser medidos antes de existir a base
persistida. Os veículos marcados como confiáveis são os que têm redação identificável,
expediente público e política de correção — o critério é **processo editorial**, não
linha editorial: por RN-08, viés político é contexto e não altera o score.

Esta lista deve migrar para a base administrável de RF-15. Enquanto isso, qualquer
inclusão passa por revisão do grupo.
"""

from enum import Enum


class Reputacao(str, Enum):
    CONFIAVEL = "confiavel"
    MISTO = "misto"
    NAO_CONFIAVEL = "nao_confiavel"
    DESCONHECIDO = "desconhecido"


#: Nota ``s`` de S-01 por reputação. ``DESCONHECIDO`` não tem nota: por RN-06 o sinal
#: fica indisponível, em vez de punir um veículo só por ser novo na base.
SCORE_POR_REPUTACAO: dict[Reputacao, float | None] = {
    Reputacao.CONFIAVEL: 1.0,
    Reputacao.MISTO: 0.5,
    Reputacao.NAO_CONFIAVEL: 0.0,
    Reputacao.DESCONHECIDO: None,
}

BASE_CURADA: dict[str, Reputacao] = {
    # Veículos de alcance nacional com expediente e política de correção públicos.
    "g1.globo.com": Reputacao.CONFIAVEL,
    "globo.com": Reputacao.CONFIAVEL,
    "folha.uol.com.br": Reputacao.CONFIAVEL,
    "uol.com.br": Reputacao.CONFIAVEL,
    "estadao.com.br": Reputacao.CONFIAVEL,
    "oglobo.globo.com": Reputacao.CONFIAVEL,
    "bbc.com": Reputacao.CONFIAVEL,
    "bbc.co.uk": Reputacao.CONFIAVEL,
    "cnnbrasil.com.br": Reputacao.CONFIAVEL,
    "agenciabrasil.ebc.com.br": Reputacao.CONFIAVEL,
    "nexojornal.com.br": Reputacao.CONFIAVEL,
    "poder360.com.br": Reputacao.CONFIAVEL,
    "reuters.com": Reputacao.CONFIAVEL,
    "apnews.com": Reputacao.CONFIAVEL,
    # Agências de checagem signatárias da IFCN — ativam RN-01.
    "lupa.uol.com.br": Reputacao.CONFIAVEL,
    "aosfatos.org": Reputacao.CONFIAVEL,
    "projetocomprova.com.br": Reputacao.CONFIAVEL,
    "boatos.org": Reputacao.CONFIAVEL,
    "e-farsas.com": Reputacao.CONFIAVEL,
}

#: Agências signatárias da IFCN: uma checagem publicada por elas aciona RN-01.
AGENCIAS_IFCN: frozenset[str] = frozenset(
    {
        "lupa.uol.com.br",
        "aosfatos.org",
        "projetocomprova.com.br",
        "estadao.com.br",  # Estadão Verifica
        "g1.globo.com",  # Fato ou Fake
    }
)


def normalizar_dominio(url_ou_dominio: str | None) -> str | None:
    """Extrai o domínio de uma URL e remove ``www.``.

    Devolve ``None`` para entrada vazia ou sem host, para que o chamador trate a
    ausência em vez de comparar contra string vazia.
    """
    if not url_ou_dominio:
        return None
    valor = url_ou_dominio.strip().lower()
    if "://" in valor:
        valor = valor.split("://", 1)[1]
    valor = valor.split("/", 1)[0].split("?", 1)[0]
    if valor.startswith("www."):
        valor = valor[4:]
    return valor or None


def reputacao(url_ou_dominio: str | None) -> Reputacao:
    """Consulta a base curada, casando também subdomínios de um veículo conhecido."""
    dominio = normalizar_dominio(url_ou_dominio)
    if not dominio:
        return Reputacao.DESCONHECIDO
    if dominio in BASE_CURADA:
        return BASE_CURADA[dominio]
    for conhecido, rep in BASE_CURADA.items():
        if dominio.endswith("." + conhecido):
            return rep
    return Reputacao.DESCONHECIDO


def e_confiavel(url_ou_dominio: str | None) -> bool:
    """Atalho para S-11/RF-28: este veículo conta como confiável na corroboração?"""
    return reputacao(url_ou_dominio) is Reputacao.CONFIAVEL
