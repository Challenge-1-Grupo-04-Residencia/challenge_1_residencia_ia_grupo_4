"""Testes do histórico de checagens (RF-42, RF-43)."""

from src.core.entities.checagem_registrada import (
    TAMANHO_DO_TRECHO,
    ChecagemRegistrada,
)
from src.infrastructure.storage.historico_memoria import HistoricoEmMemoria


def checagem(id_checagem: str, trecho: str = "Uma notícia qualquer"):
    return ChecagemRegistrada(
        id=id_checagem,
        trecho=trecho,
        veracidade=50.0,
        faixa="Inconclusiva",
        confianca=0.3,
        camada_parada="N3",
    )


class TestResumo:
    def test_texto_curto_fica_inteiro(self):
        assert ChecagemRegistrada.resumir("Notícia curta.") == "Notícia curta."

    def test_texto_longo_e_cortado(self):
        resumo = ChecagemRegistrada.resumir("palavra " * 200)

        assert len(resumo) <= TAMANHO_DO_TRECHO + 1
        assert resumo.endswith("…")

    def test_nao_parte_palavra_no_meio(self):
        texto = "antidisestablishmentarianismo " * 20
        resumo = ChecagemRegistrada.resumir(texto)

        assert not resumo.rstrip("…").endswith("antidis")

    def test_normaliza_espacos_e_quebras(self):
        assert ChecagemRegistrada.resumir("a\n\n  b\t c") == "a b c"


class TestHistoricoEmMemoria:
    def test_recupera_o_que_guardou(self):
        historico = HistoricoEmMemoria()
        historico.registrar(checagem("abc"))

        assert historico.buscar("abc") is not None

    def test_id_inexistente_devolve_none(self):
        assert HistoricoEmMemoria().buscar("nao-existe") is None

    def test_recentes_vem_do_mais_novo_ao_mais_antigo(self):
        historico = HistoricoEmMemoria()
        for i in range(3):
            historico.registrar(checagem(f"id{i}"))

        assert [c.id for c in historico.recentes()] == ["id2", "id1", "id0"]

    def test_respeita_o_limite(self):
        historico = HistoricoEmMemoria()
        for i in range(5):
            historico.registrar(checagem(f"id{i}"))

        assert len(historico.recentes(limite=2)) == 2

    def test_descarta_as_mais_antigas_ao_encher(self):
        """Sem teto, um servidor de longa duração cresceria sem limite."""
        historico = HistoricoEmMemoria(capacidade=3)
        for i in range(5):
            historico.registrar(checagem(f"id{i}"))

        assert [c.id for c in historico.recentes()] == ["id4", "id3", "id2"]
        assert historico.buscar("id0") is None

    def test_registrar_o_mesmo_id_atualiza_sem_duplicar(self):
        historico = HistoricoEmMemoria()
        historico.registrar(checagem("abc", "primeira versão"))
        historico.registrar(checagem("abc", "segunda versão"))

        assert len(historico.recentes()) == 1
        assert historico.buscar("abc").trecho == "segunda versão"

    def test_historico_vazio_devolve_lista_vazia(self):
        assert HistoricoEmMemoria().recentes() == []
