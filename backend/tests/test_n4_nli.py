"""Testes da camada N4 · inferência lógica de evidências (RF-30, S-12)."""

import pytest

from src.core.engine.n4_nli import CamadaN4Inferencia
from src.core.entities.claim import NoticiaRequest


class APIFalsa:
    """Mock do Ollama HTTP para testar a matemática do S-12 sem latência."""
    def __init__(self, vereditos: list[tuple[str, str]]):
        self.vereditos = list(vereditos)
        self.chamadas: list[str] = []

    def __call__(self, prompt: str):
        self.chamadas.append(prompt)
        if not self.vereditos:
            return {"veredicto": "NEUTRAL", "explicacao": "Fim do mock"}
        rotulo, explicacao = self.vereditos.pop(0)
        return {"veredicto": rotulo, "explicacao": explicacao}


def noticia_com(evidencias: list[str], texto: str = "A alegação do texto."):
    n = NoticiaRequest(texto=texto)
    n.resultado.evidencias = evidencias
    return n


def sinal(resultado, id_sinal: str):
    return next(s for s in resultado.sinais if s.id == id_sinal)


# =========================================================
# TESTES UNITÁRIOS (Validam a Matemática do Sinal S-12)
# =========================================================

def test_sem_evidencias_deixa_s12_indisponivel():
    """Não conseguir julgar não é julgar que a notícia é falsa (RN-06)."""
    camada = CamadaN4Inferencia(APIFalsa([]))
    noticia = camada.processar(noticia_com([]))

    assert sinal(noticia.resultado, "S-12").score is None
    assert noticia.resultado.camada_atual == "N4"


def test_evidencias_todas_neutras_deixam_s12_indisponivel():
    """Neutro não é meio-termo entre sustentar e contradizer: é ausência de dado."""
    camada = CamadaN4Inferencia(
        APIFalsa([("NEUTRAL", "Não sei")])
    )
    noticia = camada.processar(noticia_com(["evidência um", "evidência dois"]))
    assert sinal(noticia.resultado, "S-12").score is None


def test_evidencias_que_sustentam_dao_score_maximo():
    camada = CamadaN4Inferencia(
        APIFalsa([("ENTAILMENT", "Confirma!")])
    )
    noticia = camada.processar(noticia_com(["evidência um", "evidência dois"]))
    assert sinal(noticia.resultado, "S-12").score == 1.0


def test_evidencias_que_contradizem_zeram_o_score():
    camada = CamadaN4Inferencia(
        APIFalsa([("CONTRADICTION", "Refuta!")])
    )
    noticia = camada.processar(noticia_com(["evidência um", "evidência dois"]))
    assert sinal(noticia.resultado, "S-12").score == 0.0


def test_s12_pesa_vinte_pontos():
    """É o sinal mais pesado do catálogo, e a N4 é a única que o mede."""
    camada = CamadaN4Inferencia(APIFalsa([("ENTAILMENT", "Certo")]))
    noticia = camada.processar(noticia_com(["evidência"]))
    assert sinal(noticia.resultado, "S-12").peso == 20

# =========================================================
# TESTES DE INTEGRAÇÃO / LABORATÓRIO (Requer Llama 3 Rodando)
# =========================================================

# Para rodar estes no terminal de forma visual, use:
# pytest backend/tests/test_n4_nli.py -v -s -k "test_laboratorio"

CASOS_LABORATORIO = [
    (
        "A Mentira Absoluta",
        "Chá de limão com alho mata completamente o vírus da COVID-19 em 24 horas, afirma estudo vazado.",
        ["A OMS declarou que não existem provas científicas de que chás eliminem o vírus da COVID-19.", "Infectologistas alertam contra curas milagrosas."],
        "CONTRADICTION"
    ),
    (
        "A Verdade Comprovada",
        "O Brasil ganhou a medalha de ouro no futebol masculino nas Olimpíadas do Rio em 2016.",
        ["Em uma partida emocionante no Maracanã, a seleção brasileira de futebol masculino venceu a Alemanha nos pênaltis e garantiu o ouro inédito nas Olimpíadas de 2016."],
        "ENTAILMENT"
    ),
    (
        "Informação Inconclusiva (Neutralidade)",
        "O prefeito vai anunciar um novo imposto sobre bicicletas elétricas.",
        ["Câmara de vereadores debate novo projeto de lei sobre impostos veiculares, focando em carros a diesel."],
        "NEUTRAL"
    ),
    (
        "Distorção de Magnitude",
        "A bolsa de valores caiu impressionantes 50% hoje devido ao novo imposto.",
        ["O mercado financeiro fechou em leve baixa, com o principal índice recuando 2%."],
        "CONTRADICTION"
    ),
    (
        "Equivalência Semântica",
        "A capital da França baniu definitivamente o uso de patinetes elétricos nas ruas.",
        ["Paris implementou hoje a nova lei municipal proibindo a circulação de e-scooters alugados."],
        "ENTAILMENT"
    )
]

@pytest.mark.parametrize("nome,alegacao,evidencias,esperado", CASOS_LABORATORIO)
def test_laboratorio_llm_real(nome, alegacao, evidencias, esperado):
    """
    Testes reais na API do Ollama.
    Nota: Esses testes podem falhar (Timeout) se o Docker do Ollama não estiver ligado.
    """
    import urllib.request
    try:
        # Checa rápido se o Ollama está vivo na máquina
        urllib.request.urlopen("http://localhost:11434", timeout=2)
    except Exception:
        pytest.skip("Ollama não está rodando no localhost:11434. Pulando teste de integração.")

    # Usa o cliente Real (não envia o mock da APIFalsa)
    camada = CamadaN4Inferencia()
    noticia = camada.processar(noticia_com(evidencias, texto=alegacao))
    
    if esperado == "NEUTRAL":
        assert sinal(noticia.resultado, "S-12").score is None
    elif esperado == "ENTAILMENT":
        assert sinal(noticia.resultado, "S-12").score == 1.0
    else: # CONTRADICTION
        assert sinal(noticia.resultado, "S-12").score == 0.0
