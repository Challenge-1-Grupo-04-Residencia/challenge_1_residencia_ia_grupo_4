"""Testes da camada N4 · inferência lógica de evidências (RF-30, S-12).

Todos usam duplo do provedor de LLM. Os cinco testes "de laboratório" que existiam aqui
batiam no Ollama de verdade e davam ``skip`` quando ele não estava rodando — ou seja, a
camada que mede o sinal mais pesado do catálogo ficava com **zero** cobertura de teste
na máquina de quem não tinha o Docker ligado, e na CI. Teste não toca a rede, por
convenção do projeto; os casos de laboratório viraram
``backend/tests/laboratorio_n4.py``, que é script e não suíte.
"""

import pytest

from src.core.engine.n4_nli import (
    ROTULO_CONTRADIZ,
    ROTULO_NEUTRO,
    ROTULO_SUSTENTA,
    CamadaN4Inferencia,
    ErroDoProvedor,
)
from src.core.entities.claim import NoticiaRequest


class ProvedorFalso:
    """Duplo do provedor: devolve os vereditos combinados e grava o prompt recebido."""

    def __init__(self, vereditos: list[str], motivo: str = "motivo de teste"):
        self.vereditos = vereditos
        self.motivo = motivo
        self.chamadas: list[str] = []

    def __call__(self, prompt: str) -> dict:
        self.chamadas.append(prompt)
        return {
            "vereditos": [
                {"indice": i, "veredicto": rotulo, "motivo": self.motivo}
                for i, rotulo in enumerate(self.vereditos)
            ]
        }


class ProvedorQueFalha:
    def __init__(self, mensagem: str = "conexão recusada"):
        self.mensagem = mensagem

    def __call__(self, prompt: str) -> dict:
        raise ErroDoProvedor(self.mensagem)


class ProvedorCru:
    """Devolve exatamente o que lhe foi dado, para testar parsing malformado."""

    def __init__(self, resposta):
        self.resposta = resposta

    def __call__(self, prompt: str):
        return self.resposta


def noticia_com(evidencias: list[str], texto: str = "A alegação do texto."):
    noticia = NoticiaRequest(texto=texto)
    noticia.resultado.evidencias = evidencias
    return noticia


def sinal(resultado, id_sinal: str):
    return next(s for s in resultado.sinais if s.id == id_sinal)


class TestMatematicaDoS12:
    def test_sem_evidencias_deixa_s12_indisponivel(self):
        """Não conseguir julgar não é julgar que a notícia é falsa (RN-06)."""
        camada = CamadaN4Inferencia(ProvedorFalso([]))
        noticia = camada.processar(noticia_com([]))

        assert sinal(noticia.resultado, "S-12").score is None
        assert noticia.resultado.camada_atual == "N4"

    def test_todas_neutras_deixam_s12_indisponivel(self):
        """Neutro não é meio-termo entre sustentar e contradizer: é ausência de dado."""
        camada = CamadaN4Inferencia(ProvedorFalso([ROTULO_NEUTRO, ROTULO_NEUTRO]))
        noticia = camada.processar(noticia_com(["evidência um", "evidência dois"]))

        assert sinal(noticia.resultado, "S-12").score is None

    def test_todas_sustentam_dao_score_maximo(self):
        camada = CamadaN4Inferencia(ProvedorFalso([ROTULO_SUSTENTA, ROTULO_SUSTENTA]))
        noticia = camada.processar(noticia_com(["uma", "duas"]))

        assert sinal(noticia.resultado, "S-12").score == 1.0

    def test_todas_contradizem_zeram_o_score(self):
        camada = CamadaN4Inferencia(ProvedorFalso([ROTULO_CONTRADIZ, ROTULO_CONTRADIZ]))
        noticia = camada.processar(noticia_com(["uma", "duas"]))

        assert sinal(noticia.resultado, "S-12").score == 0.0

    def test_score_e_gradiente_e_nao_moeda(self):
        """O conserto principal desta camada: três a um dá 0,75, não 1,0.

        Com um veredito único para o bloco inteiro, S-12 só podia valer 0,0 ou 1,0 — e
        com peso 20 ele sozinho movia o score final em 32 pontos.
        """
        camada = CamadaN4Inferencia(
            ProvedorFalso(
                [ROTULO_SUSTENTA, ROTULO_SUSTENTA, ROTULO_SUSTENTA, ROTULO_CONTRADIZ]
            )
        )
        noticia = camada.processar(noticia_com(["a", "b", "c", "d"]))

        assert sinal(noticia.resultado, "S-12").score == pytest.approx(0.75)

    def test_neutras_nao_entram_no_denominador(self):
        """Uma que sustenta e três que não tratam do assunto é 1,0, não 0,25."""
        camada = CamadaN4Inferencia(
            ProvedorFalso([ROTULO_SUSTENTA, ROTULO_NEUTRO, ROTULO_NEUTRO, ROTULO_NEUTRO])
        )
        noticia = camada.processar(noticia_com(["a", "b", "c", "d"]))

        assert sinal(noticia.resultado, "S-12").score == 1.0

    def test_empate_entre_sustentar_e_contradizer_da_meio(self):
        camada = CamadaN4Inferencia(ProvedorFalso([ROTULO_SUSTENTA, ROTULO_CONTRADIZ]))
        noticia = camada.processar(noticia_com(["a", "b"]))

        assert sinal(noticia.resultado, "S-12").score == pytest.approx(0.5)
        assert "se dividem" in noticia.resultado.explicacao

    def test_s12_pesa_vinte_pontos(self):
        """É o sinal mais pesado do catálogo, e a N4 é a única que o mede."""
        camada = CamadaN4Inferencia(ProvedorFalso([ROTULO_SUSTENTA]))
        noticia = camada.processar(noticia_com(["evidência"]))

        assert sinal(noticia.resultado, "S-12").peso == 20


class TestUmaChamadaSo:
    def test_uma_unica_chamada_para_todas_as_evidencias(self):
        """A latência da camada mais cara não pode crescer com o número de evidências."""
        provedor = ProvedorFalso([ROTULO_SUSTENTA] * 5)
        camada = CamadaN4Inferencia(provedor)
        camada.processar(noticia_com(["a", "b", "c", "d", "e"]))

        assert len(provedor.chamadas) == 1

    def test_prompt_numera_as_evidencias(self):
        provedor = ProvedorFalso([ROTULO_SUSTENTA, ROTULO_SUSTENTA])
        camada = CamadaN4Inferencia(provedor)
        camada.processar(noticia_com(["primeira coisa", "segunda coisa"]))

        prompt = provedor.chamadas[0]
        assert "0. primeira coisa" in prompt
        assert "1. segunda coisa" in prompt

    def test_limita_o_numero_de_evidencias_enviadas(self):
        from src.core.engine.n4_nli import MAXIMO_DE_EVIDENCIAS

        provedor = ProvedorFalso([ROTULO_SUSTENTA])
        camada = CamadaN4Inferencia(provedor)
        camada.processar(noticia_com([f"evidência {i}" for i in range(20)]))

        enviadas = provedor.chamadas[0].count("\n")
        assert f"{MAXIMO_DE_EVIDENCIAS - 1}. evidência" in provedor.chamadas[0]
        assert f"{MAXIMO_DE_EVIDENCIAS}. evidência" not in provedor.chamadas[0]
        assert enviadas > 0


class TestFalhaDoProvedor:
    def test_provedor_fora_do_ar_deixa_s12_indisponivel(self):
        """Falha nossa não é evidência contra a notícia (RN-06)."""
        camada = CamadaN4Inferencia(ProvedorQueFalha())
        noticia = camada.processar(noticia_com(["uma evidência"]))

        assert sinal(noticia.resultado, "S-12").score is None

    def test_erro_tecnico_nao_vaza_para_a_explicacao(self):
        """RN-11: a persona não lê stack trace ao usuário.

        Antes, a explicação entregue na tela continha literalmente
        ``(IA: Erro na API Ollama: <urlopen error [Errno 61] Connection refused>)``.
        """
        camada = CamadaN4Inferencia(
            ProvedorQueFalha("<urlopen error [Errno 61] Connection refused>")
        )
        noticia = camada.processar(noticia_com(["uma evidência"]))

        explicacao = noticia.resultado.explicacao
        justificativa = sinal(noticia.resultado, "S-12").justificativa
        for vazamento in ("Errno", "urlopen", "Traceback", "Exception"):
            assert vazamento not in explicacao
            assert vazamento not in justificativa

    def test_falha_do_provedor_e_diferente_de_evidencia_neutra(self):
        """As duas deixam S-12 indisponível, mas a justificativa não pode confundir."""
        falhou = CamadaN4Inferencia(ProvedorQueFalha()).processar(
            noticia_com(["uma"])
        )
        neutro = CamadaN4Inferencia(ProvedorFalso([ROTULO_NEUTRO])).processar(
            noticia_com(["uma"])
        )

        assert sinal(falhou.resultado, "S-12").justificativa != sinal(
            neutro.resultado, "S-12"
        ).justificativa
        assert "não respondeu" in sinal(falhou.resultado, "S-12").justificativa
        assert "neutras" in sinal(neutro.resultado, "S-12").justificativa


class TestRespostaMalformada:
    def test_lista_crua_e_aceita(self):
        camada = CamadaN4Inferencia(
            ProvedorCru([{"veredicto": ROTULO_SUSTENTA}, {"veredicto": ROTULO_CONTRADIZ}])
        )
        noticia = camada.processar(noticia_com(["a", "b"]))

        assert sinal(noticia.resultado, "S-12").score == pytest.approx(0.5)

    def test_formato_antigo_de_veredito_unico_ainda_funciona(self):
        """Compatibilidade: modelo que responde um rótulo só para o bloco."""
        camada = CamadaN4Inferencia(
            ProvedorCru({"veredicto": ROTULO_CONTRADIZ, "explicacao": "refuta"})
        )
        noticia = camada.processar(noticia_com(["a", "b"]))

        assert sinal(noticia.resultado, "S-12").score == 0.0

    def test_rotulo_desconhecido_e_descartado_e_nao_vira_neutro(self):
        """Contar lixo como neutro seria fabricar medição."""
        camada = CamadaN4Inferencia(
            ProvedorCru({"vereditos": [{"veredicto": "TALVEZ"}, {"veredicto": "SIM"}]})
        )
        noticia = camada.processar(noticia_com(["a", "b"]))

        assert sinal(noticia.resultado, "S-12").score is None
        assert "utilizável" in sinal(noticia.resultado, "S-12").justificativa

    def test_json_sem_o_campo_esperado_deixa_s12_indisponivel(self):
        camada = CamadaN4Inferencia(ProvedorCru({"resposta": "sei lá"}))
        noticia = camada.processar(noticia_com(["a"]))

        assert sinal(noticia.resultado, "S-12").score is None

    def test_tipo_inesperado_nao_derruba_a_camada(self):
        camada = CamadaN4Inferencia(ProvedorCru("uma string qualquer"))
        noticia = camada.processar(noticia_com(["a"]))

        assert sinal(noticia.resultado, "S-12").score is None
