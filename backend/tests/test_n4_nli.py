"""Testes da camada N4 · inferência lógica de evidências (RF-30, S-12)."""

import pytest

from src.core.engine.n4_nli import CamadaN4Inferencia
from src.core.entities.claim import NoticiaRequest


class ClassificadorFalso:
    """NLI controlado, para testar sem baixar o mDeBERTa.

    Recebe a lista de vereditos a devolver, em ordem, e registra os pares que viu.
    """

    def __init__(self, vereditos: list[tuple[str, float]]):
        self.vereditos = list(vereditos)
        self.chamadas: list[dict] = []

    def __call__(self, par: dict):
        self.chamadas.append(par)
        rotulo, score = self.vereditos.pop(0)
        return {"label": rotulo, "score": score}


def noticia_com(evidencias: list[str], texto: str = "A alegação do texto."):
    n = NoticiaRequest(texto=texto)
    n.resultado.evidencias = evidencias
    return n


def sinal(resultado, id_sinal: str):
    return next(s for s in resultado.sinais if s.id == id_sinal)


def test_sem_evidencias_deixa_s12_indisponivel():
    """Não conseguir julgar não é julgar que a notícia é falsa (RN-06)."""
    camada = CamadaN4Inferencia(ClassificadorFalso([]))
    noticia = camada.processar(noticia_com([]))

    assert sinal(noticia.resultado, "S-12").score is None
    assert noticia.resultado.camada_atual == "N4"


def test_evidencias_todas_neutras_deixam_s12_indisponivel():
    """Neutro não é meio-termo entre sustentar e contradizer: é ausência de dado."""
    camada = CamadaN4Inferencia(
        ClassificadorFalso([("NEUTRAL", 0.9), ("NEUTRAL", 0.95)])
    )
    noticia = camada.processar(noticia_com(["evidência um", "evidência dois"]))

    assert sinal(noticia.resultado, "S-12").score is None


def test_evidencias_que_sustentam_dao_score_maximo():
    camada = CamadaN4Inferencia(
        ClassificadorFalso([("ENTAILMENT", 0.9), ("ENTAILMENT", 0.85)])
    )
    noticia = camada.processar(noticia_com(["evidência um", "evidência dois"]))

    assert sinal(noticia.resultado, "S-12").score == 1.0


def test_evidencias_que_contradizem_zeram_o_score():
    camada = CamadaN4Inferencia(
        ClassificadorFalso([("CONTRADICTION", 0.9), ("CONTRADICTION", 0.88)])
    )
    noticia = camada.processar(noticia_com(["evidência um", "evidência dois"]))

    assert sinal(noticia.resultado, "S-12").score == 0.0


def test_score_e_a_proporcao_que_sustenta():
    """Fórmula de S-12: sustenta / (sustenta + contradiz)."""
    camada = CamadaN4Inferencia(
        ClassificadorFalso(
            [("ENTAILMENT", 0.9), ("ENTAILMENT", 0.9), ("CONTRADICTION", 0.9)]
        )
    )
    noticia = camada.processar(noticia_com(["um", "dois", "três"]))

    assert sinal(noticia.resultado, "S-12").score == pytest.approx(2 / 3)


def test_veredito_de_baixa_confianca_e_descartado():
    """NLI em português erra bastante; veredito fraco não move o sinal mais pesado."""
    camada = CamadaN4Inferencia(
        ClassificadorFalso([("CONTRADICTION", 0.4), ("ENTAILMENT", 0.9)])
    )
    noticia = camada.processar(noticia_com(["fraca", "forte"]))

    # A contradição de confiança 0,4 foi ignorada, sobrou só a que sustenta.
    assert sinal(noticia.resultado, "S-12").score == 1.0


def test_evidencia_entra_como_premissa_e_alegacao_como_hipotese():
    """A pergunta é se a evidência publicada implica a alegação, não o contrário."""
    classificador = ClassificadorFalso([("ENTAILMENT", 0.9)])
    camada = CamadaN4Inferencia(classificador)
    camada.processar(noticia_com(["a evidência"], texto="a alegação"))

    assert classificador.chamadas[0] == {
        "text": "a evidência",
        "text_pair": "a alegação",
    }


def test_s12_pesa_vinte_pontos():
    """É o sinal mais pesado do catálogo, e a N4 é a única que o mede."""
    camada = CamadaN4Inferencia(ClassificadorFalso([("ENTAILMENT", 0.9)]))
    noticia = camada.processar(noticia_com(["evidência"]))

    assert sinal(noticia.resultado, "S-12").peso == 20
