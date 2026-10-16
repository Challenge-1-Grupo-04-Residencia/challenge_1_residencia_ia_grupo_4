"""Testes da API HTTP, com o pipeline substituído por camadas controladas."""

import pytest
from fastapi.testclient import TestClient

from src.core.engine.n2_content import CamadaN2Conteudo
from src.core.engine.n3_corroboration import CamadaN3Corroboracao
from src.core.engine.orchestrator import Orquestrador
from src.main import app


class BuscadorSemRede:
    """Evita bater no GDELT durante os testes."""

    def buscar(self, texto: str, top_k: int = 5):
        return []


def test_health_responde_ok():
    with TestClient(app) as c:
        resposta = c.get("/health")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"


def test_texto_vazio_e_rejeitado():
    with TestClient(app) as c:
        resposta = c.post("/api/v1/checar", json={"texto": ""})

    assert resposta.status_code == 422


def test_checagem_devolve_campos_obrigatorios_de_rn05(monkeypatch):
    """RN-05: todo resultado traz faixa, sinais e fontes. Sem explicação não exibe."""
    n2 = CamadaN2Conteudo()
    n3 = CamadaN3Corroboracao(BuscadorSemRede())
    n2.set_proxima(n3)
    monkeypatch.setattr("src.main.obter_orquestrador", lambda: Orquestrador(n2))

    with TestClient(app) as c:
        resposta = c.post(
            "/api/v1/checar",
            json={
                "texto": (
                    "URGENTE!!! REPASSEM!!! O governo quer controlar a população "
                    "com as vacinas que contêm chip!!! Acordem!!!"
                )
            },
        )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["faixa"]
    assert corpo["explicacao"]
    assert corpo["sinais"]
    assert 0.0 <= corpo["confianca"] <= 1.0
    assert 0.0 <= corpo["cobertura"] <= 1.0


def test_sinais_trazem_peso_e_dimensao_para_rf33(monkeypatch):
    """RF-33: o usuário pode consultar o detalhamento de cada sinal e do seu peso."""
    n2 = CamadaN2Conteudo()
    monkeypatch.setattr("src.main.obter_orquestrador", lambda: Orquestrador(n2))

    with TestClient(app) as c:
        corpo = c.post(
            "/api/v1/checar",
            json={"texto": "Nesta terça o Ministério da Saúde anunciou a campanha nacional de vacinação."},
        ).json()

    for sinal in corpo["sinais"]:
        assert sinal["peso"] > 0
        assert sinal["dimensao"] in ("fonte", "conteudo", "corroboracao")
        assert sinal["id"].startswith("S-")


class TestFeedEAcompanhamento:
    """Rotas de feed (RF-43) e de perguntas de acompanhamento (RF-04)."""

    @pytest.fixture(autouse=True)
    def historico_limpo(self):
        """Cada teste começa com o histórico vazio.

        O histórico é um singleton em ``lru_cache``: sem limpar, uma checagem feita em
        um teste apareceria no feed de outro.
        """
        from src.main import obter_historico

        obter_historico.cache_clear()
        yield
        obter_historico.cache_clear()

    # O texto tem de passar de MINIMO_DE_PALAVRAS: abaixo disso a N2 deixa todos os
    # sinais de estilo indisponíveis, e não há o que a Vera responda sobre a escrita.
    TEXTO_PADRAO = (
        "Nesta terça-feira o Ministério da Saúde anunciou a nova campanha nacional de "
        "vacinação contra a gripe, que deve atender os grupos prioritários a partir do "
        "mês que vem em todas as unidades básicas do país."
    )

    def _checar(self, client, texto=TEXTO_PADRAO):
        n2 = CamadaN2Conteudo()
        n2.set_proxima(CamadaN3Corroboracao(BuscadorSemRede()))
        return client.post("/api/v1/checar", json={"texto": texto})

    def test_checagem_devolve_id(self, monkeypatch):
        n2 = CamadaN2Conteudo()
        monkeypatch.setattr("src.main.obter_orquestrador", lambda: Orquestrador(n2))

        with TestClient(app) as c:
            corpo = self._checar(c).json()

        assert corpo["id"]

    def test_feed_comeca_vazio(self):
        with TestClient(app) as c:
            assert c.get("/api/v1/checagens/recentes").json() == []

    def test_checagem_entra_no_feed(self, monkeypatch):
        n2 = CamadaN2Conteudo()
        monkeypatch.setattr("src.main.obter_orquestrador", lambda: Orquestrador(n2))

        with TestClient(app) as c:
            self._checar(c)
            feed = c.get("/api/v1/checagens/recentes").json()

        assert len(feed) == 1
        assert feed[0]["faixa"]
        assert feed[0]["trecho"]

    def test_feed_vem_do_mais_novo_ao_mais_antigo(self, monkeypatch):
        n2 = CamadaN2Conteudo()
        monkeypatch.setattr("src.main.obter_orquestrador", lambda: Orquestrador(n2))

        with TestClient(app) as c:
            self._checar(c, "Primeira notícia sobre vacinação nacional contra a gripe.")
            self._checar(c, "Segunda notícia sobre o orçamento federal deste ano.")
            feed = c.get("/api/v1/checagens/recentes").json()

        assert feed[0]["trecho"].startswith("Segunda")

    def test_feed_respeita_o_limite(self, monkeypatch):
        n2 = CamadaN2Conteudo()
        monkeypatch.setattr("src.main.obter_orquestrador", lambda: Orquestrador(n2))

        with TestClient(app) as c:
            for i in range(3):
                self._checar(c, f"Notícia número {i} sobre a campanha de vacinação nacional.")
            feed = c.get("/api/v1/checagens/recentes?limite=2").json()

        assert len(feed) == 2

    def test_pergunta_sobre_checagem_inexistente_da_404(self):
        with TestClient(app) as c:
            resposta = c.post(
                "/api/v1/perguntar",
                json={"id_checagem": "nao-existe", "pergunta": "por quê?"},
            )

        assert resposta.status_code == 404

    def test_pergunta_usa_o_contexto_da_checagem(self, monkeypatch):
        """RF-04: responde sobre o resultado já entregue, sem refazer a checagem."""
        n2 = CamadaN2Conteudo()
        monkeypatch.setattr("src.main.obter_orquestrador", lambda: Orquestrador(n2))

        with TestClient(app) as c:
            id_checagem = self._checar(c).json()["id"]
            corpo = c.post(
                "/api/v1/perguntar",
                json={"id_checagem": id_checagem, "pergunta": "como o texto foi escrito?"},
            ).json()

        assert corpo["assunto"] == "estilo"
        assert corpo["texto"]
        assert corpo["sinais_citados"]

    def test_pergunta_vazia_e_rejeitada(self):
        with TestClient(app) as c:
            resposta = c.post(
                "/api/v1/perguntar", json={"id_checagem": "x", "pergunta": ""}
            )

        assert resposta.status_code == 422
