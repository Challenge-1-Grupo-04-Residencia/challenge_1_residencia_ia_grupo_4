"""Testes da API HTTP, com o pipeline substituído por camadas controladas."""

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
