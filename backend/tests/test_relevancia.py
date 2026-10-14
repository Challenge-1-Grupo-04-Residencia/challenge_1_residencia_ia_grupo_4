"""Testes da relevância textual da N3 (issue #73).

A medida existe para barrar o documento que só divide o assunto geral da alegação. Os
casos vêm de falhas reais: "taxa das blusinhas" chegando como evidência de "lula vai
taxar o pix", e "lula lamenta morte de fundadora" sendo lido como "lula morreu".
"""

import pytest

from src.core.engine.relevancia import relevancia
from src.core.engine.n3_corroboration import LIMIAR_DE_RELEVANCIA


def test_identico_e_maximo():
    assert relevancia("Lula morreu", "Lula morreu") == pytest.approx(1.0)


def test_sem_palavra_de_conteudo_em_comum_e_zero():
    assert relevancia("A Selic subiu", "o time venceu o campeonato") == 0.0


def test_texto_vazio_e_zero():
    assert relevancia("", "qualquer coisa") == 0.0
    assert relevancia("Lula morreu", "") == 0.0


def test_so_palavras_de_funcao_nao_contam():
    # "de o a que" são palavras vazias: nenhuma sobreposição de conteúdo.
    assert relevancia("de o a que", "de a o que") == 0.0


class TestCasosReais:
    """Separa o fato igual do assunto apenas parecido, no limiar da N3."""

    def test_assunto_parecido_fato_diferente_fica_abaixo_do_limiar(self):
        # "taxa das blusinhas" divide "lula" e o tema tributo, mas não é "taxar o pix".
        r = relevancia(
            "lula vai taxar o pix",
            "Taxa das blusinhas: Lula sanciona MP que acaba com cobrança",
        )
        assert r < LIMIAR_DE_RELEVANCIA

    def test_lamenta_morte_fica_abaixo_da_corroboracao_de_verdade(self):
        # "lula lamenta morte de fundadora" divide só "lula": fica bem abaixo de uma
        # corroboração que divide o fato. A porta da N3 não precisa cravar este caso —
        # a confusão sujeito/ação é trabalho do juiz da N4 —, mas a relevância tem de
        # ordená-lo abaixo do desmentido que realmente fala do boato.
        lamenta = relevancia("o lula morreu", "Lula lamenta morte de fundadora do PT")
        desmentido = relevancia(
            "o lula morreu", "Como a teoria falsa de que Lula morreu ameaça a democracia"
        )
        assert lamenta < desmentido

    def test_mesmo_fato_fica_acima_do_limiar(self):
        # Corroboração verdadeira: compartilha os termos que carregam o fato.
        r = relevancia(
            "O Copom reduziu a Selic para 14,25% ao ano em junho de 2026",
            "Copom realiza o terceiro corte na taxa de juros em 2026: Selic vai a 14,25%",
        )
        assert r >= LIMIAR_DE_RELEVANCIA

    def test_desmentido_compartilha_o_fato_e_passa(self):
        # A meta-checagem precisa CHEGAR à N4 para ser lida como contradição.
        r = relevancia(
            "o lula morreu",
            "Como a teoria falsa de que Lula morreu ameaça a democracia",
        )
        assert r >= LIMIAR_DE_RELEVANCIA
