"""Testes do BuscadorHibrido: resiliência a fonte fora do ar (RN-06).

Uma fonte indisponível não pode derrubar as demais — era o que fazia a N3 dizer
"não consegui procurar" mesmo com o banco vetorial local de pé. Só quando *todas* as
fontes caem é que o híbrido fica indisponível.

Dependências externas são dubladas: nenhum teste toca a rede nem o banco.
"""

import pytest

from src.core.entities.claim import DocumentoRelacionado
from src.core.ports.news_search import BuscaIndisponivel
from src.infrastructure.search.hibrido_search import BuscadorHibrido


def _doc(similaridade: float) -> DocumentoRelacionado:
    return DocumentoRelacionado(
        titulo="notícia",
        url="https://exemplo.test",
        fonte="fonte",
        similaridade=similaridade,
        fonte_confiavel=True,
    )


class _BuscadorFake:
    """Fonte que devolve uma lista fixa (lista vazia = procurou e não achou)."""

    def __init__(self, resultados: list[DocumentoRelacionado]):
        self._resultados = resultados

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        return self._resultados


class _BuscadorQueCai:
    """Fonte sempre indisponível (rede fora, limite estourado)."""

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        raise BuscaIndisponivel("fonte fora do ar")


def test_fonte_fora_nao_derruba_as_demais():
    # Google Notícias cai, mas o Vetorial local responde: o resultado dele sobrevive.
    hibrido = BuscadorHibrido([_BuscadorQueCai(), _BuscadorFake([_doc(0.9)])])

    resultados = hibrido.buscar("lula morreu")

    assert len(resultados) == 1
    assert resultados[0].similaridade == 0.9


def test_fonte_fora_e_outra_sem_achados_e_procura_vazia_nao_indisponivel():
    # Uma fonte caiu e a outra procurou sem achar: isso é "procurei e não achei"
    # (lista vazia), nunca indisponibilidade.
    hibrido = BuscadorHibrido([_BuscadorQueCai(), _BuscadorFake([])])

    assert hibrido.buscar("lula morreu") == []


def test_todas_indisponiveis_levanta_indisponivel():
    hibrido = BuscadorHibrido([_BuscadorQueCai(), _BuscadorQueCai()])

    with pytest.raises(BuscaIndisponivel):
        hibrido.buscar("lula morreu")


def test_junta_fontes_ordena_por_similaridade_e_corta_top_k():
    hibrido = BuscadorHibrido(
        [_BuscadorFake([_doc(0.5), _doc(0.95)]), _BuscadorFake([_doc(0.8)])]
    )

    resultados = hibrido.buscar("qualquer", top_k=2)

    assert [r.similaridade for r in resultados] == [0.95, 0.8]
