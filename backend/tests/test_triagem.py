"""Testes da triagem de entrada (RF-01, RF-02, RF-26).

A Vera é um chat: ela recebe "oi, tudo bem?" tanto quanto recebe notícia. Sem triagem, o
pipeline tratava a saudação como alegação de fato e devolvia **77% de veracidade** para
um "Oi, tudo bem?" — além de gastar uma busca no GDELT e uma chamada de LLM por cada
cumprimento recebido.
"""

import pytest
from fastapi.testclient import TestClient

from src.core.engine import business_rules, triagem
from src.core.engine.n2_content import CamadaN2Conteudo
from src.core.engine.n3_corroboration import CamadaN3Corroboracao
from src.core.engine.orchestrator import Orquestrador
from src.core.engine.scoring import Faixa
from src.core.engine.triagem import Natureza
from src.core.entities.claim import NoticiaRequest
from src.main import app


class TestClassificacao:
    @pytest.mark.parametrize(
        "texto",
        [
            "Oi",
            "oi!",
            "Olá",
            "Bom dia",
            "Boa tarde!",
            "e aí",
            "opa",
        ],
    )
    def test_saudacao_nao_e_alegacao(self, texto):
        assert triagem.classificar(texto) is not Natureza.ALEGACAO

    @pytest.mark.parametrize(
        "texto",
        [
            "Oi, tudo bem?",
            "quem é você?",
            "o que você faz?",
            "qual seu nome",
            "pode me ajudar?",
            "Bom dia Vera, como você está hoje? Queria saber se você pode me ajudar "
            "com uma coisa.",
            "teste",
            "kkkk",
            "?",
        ],
    )
    def test_conversa_nao_e_alegacao(self, texto):
        assert triagem.classificar(texto) is Natureza.CONVERSA

    @pytest.mark.parametrize(
        "texto", ["obrigada!", "valeu", "muito obrigado, Vera", "tchau"]
    )
    def test_agradecimento_nao_e_alegacao(self, texto):
        assert triagem.classificar(texto) is Natureza.AGRADECIMENTO

    @pytest.mark.parametrize(
        "texto",
        [
            "URGENTE!!! REPASSEM!!! O governo quer controlar a população com vacinas "
            "que contêm chip!!!",
            "O IBGE divulgou que a taxa de desemprego ficou em 6,4% no trimestre.",
            "Chá de limão com alho mata o vírus da COVID-19 em 24 horas",
            "https://g1.globo.com/noticia",
            "O presidente aprovou a nova lei nesta semana",
        ],
    )
    def test_alegacao_vai_para_o_pipeline(self, texto):
        assert triagem.classificar(texto) is Natureza.ALEGACAO

    def test_saudacao_antes_de_pedido_de_checagem_e_alegacao(self):
        """O caso que a triagem não pode errar.

        "bom dia, isso é verdade?" começa com cumprimento e é uma checagem de verdade.
        Barrar isto seria pior do que checar uma conversa: o usuário ficaria sem a
        resposta que veio buscar.
        """
        assert (
            triagem.classificar("bom dia, essa notícia do Pix é verdade?")
            is Natureza.ALEGACAO
        )
        assert (
            triagem.classificar(
                "Olá! Vi uma mensagem dizendo que a vacina causa autismo, procede?"
            )
            is Natureza.ALEGACAO
        )

    def test_texto_longo_e_sempre_alegacao(self):
        """Ninguém escreve dois parágrafos de conversa fiada para um checador."""
        longo = " ".join(["palavra"] * 40)

        assert triagem.classificar(longo) is Natureza.ALEGACAO

    def test_na_duvida_checa(self):
        """O viés é para checar: errar para o lado de não checar deixa o usuário sem
        resposta, e errar para o lado de checar custa uma resposta estranha."""
        assert triagem.classificar("o ministro pediu demissão") is Natureza.ALEGACAO

    def test_texto_vazio_nao_quebra(self):
        assert triagem.classificar("   ") is Natureza.CONVERSA


class TestRespostaDaVera:
    @pytest.mark.parametrize(
        "natureza", [Natureza.SAUDACAO, Natureza.CONVERSA, Natureza.AGRADECIMENTO]
    )
    def test_toda_natureza_de_conversa_tem_resposta(self, natureza):
        resposta = triagem.resposta_para(natureza)

        assert resposta
        assert len(resposta) > 20

    @pytest.mark.parametrize(
        "natureza", [Natureza.SAUDACAO, Natureza.CONVERSA, Natureza.AGRADECIMENTO]
    )
    def test_resposta_convida_a_mandar_noticia(self, natureza):
        """A conversa serve para chegar na checagem, não para substituí-la."""
        resposta = triagem.resposta_para(natureza).lower()

        assert any(termo in resposta for termo in ("manda", "confiro", "conferir"))


class TestVereditoDeConversa:
    def test_conversa_nao_recebe_porcentagem(self):
        """RN-03 em espírito: o que não é alegação de fato não recebe veracidade."""
        contexto = business_rules.Contexto(natureza=Natureza.SAUDACAO.value)
        veredito = business_rules.aplicar(77.0, 0.5, contexto)

        assert veredito.veracidade is None
        assert veredito.exibe_porcentagem is False
        assert veredito.faixa is Faixa.CONVERSA
        assert veredito.regra_aplicada == "TRIAGEM"

    def test_conversa_tem_explicacao(self):
        """RN-05: resultado sem explicação não é exibido."""
        contexto = business_rules.Contexto(natureza=Natureza.CONVERSA.value)

        assert business_rules.aplicar(None, 0.0, contexto).motivo_regra


class TestOrquestrador:
    def _orquestrador(self, buscador_chamado: list):
        class BuscadorEspiao:
            def buscar(self, texto, top_k=5):
                buscador_chamado.append(texto)
                return []

        n2 = CamadaN2Conteudo()
        n2.set_proxima(CamadaN3Corroboracao(BuscadorEspiao()))
        return Orquestrador(n2)

    def test_conversa_nao_roda_nenhuma_camada(self):
        """O ganho econômico da triagem: zero busca externa, zero chamada de modelo."""
        chamadas: list[str] = []
        noticia = NoticiaRequest(texto="Oi, tudo bem?")

        veredito = self._orquestrador(chamadas).veredito(noticia)

        assert chamadas == []
        assert noticia.resultado.sinais == []
        assert noticia.resultado.camada_atual == "TRIAGEM"
        assert veredito.faixa is Faixa.CONVERSA

    def test_alegacao_roda_as_camadas(self):
        chamadas: list[str] = []
        noticia = NoticiaRequest(
            texto=(
                "O Ministério da Saúde anunciou nesta terça a nova campanha nacional "
                "de vacinação contra a gripe para os grupos prioritários."
            )
        )

        self._orquestrador(chamadas).veredito(noticia)

        assert len(chamadas) == 1
        assert noticia.resultado.sinais


class TestPelaApi:
    def _orquestrador_sem_rede(self):
        class BuscadorSemRede:
            def buscar(self, texto, top_k=5):
                return []

        n2 = CamadaN2Conteudo()
        n2.set_proxima(CamadaN3Corroboracao(BuscadorSemRede()))
        return Orquestrador(n2)

    def test_saudacao_pela_api_nao_devolve_veracidade(self, monkeypatch):
        monkeypatch.setattr(
            "src.main.obter_orquestrador", self._orquestrador_sem_rede
        )

        with TestClient(app) as cliente:
            corpo = cliente.post("/api/v1/checar", json={"texto": "Oi, tudo bem?"}).json()

        assert corpo["veracidade"] is None
        assert corpo["exibe_porcentagem"] is False
        assert corpo["faixa"] == "Conversa"
        assert corpo["camada_parada"] == "TRIAGEM"
        assert corpo["sinais"] == []
        # RN-05: resultado sem explicação não é exibido.
        assert corpo["explicacao"]
