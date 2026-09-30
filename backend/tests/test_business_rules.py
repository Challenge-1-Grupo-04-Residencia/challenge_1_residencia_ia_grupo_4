"""Testes das regras que se sobrepõem ao score (RF-10, RN-01 a RN-04)."""

from src.core.engine import business_rules
from src.core.engine.business_rules import Contexto
from src.core.engine.scoring import Faixa


def test_sem_regra_ativa_o_score_calculado_prevalece():
    veredito = business_rules.aplicar(72.0, 0.8, Contexto())

    assert veredito.veracidade == 72.0
    assert veredito.faixa is Faixa.VERDADEIRA
    assert veredito.regra_aplicada is None


class TestRN01AgenciaDeChecagem:
    """O veredito de agência signatária da IFCN prevalece sobre o score."""

    def test_desmentido_derruba_score_alto(self):
        veredito = business_rules.aplicar(
            88.0, 0.9, Contexto(veredito_agencia="falso", agencia="Agência Lupa")
        )

        assert veredito.veracidade <= 10.0
        assert veredito.regra_aplicada == "RN-01"
        assert "Lupa" in veredito.motivo_regra

    def test_confirmacao_levanta_score_baixo(self):
        veredito = business_rules.aplicar(
            12.0, 0.9, Contexto(veredito_agencia="verdadeiro", agencia="Aos Fatos")
        )

        assert veredito.veracidade >= 90.0
        assert veredito.faixa is Faixa.CONFIRMADA

    def test_vence_o_alerta_de_impostor(self):
        """A agência avaliou o conteúdo concreto; o impostor é heurística de domínio."""
        veredito = business_rules.aplicar(
            50.0,
            0.8,
            Contexto(veredito_agencia="verdadeiro", dominio_impostor=True),
        )

        assert veredito.regra_aplicada == "RN-01"


class TestRN02DominioImpostor:
    def test_impostor_tem_teto_de_quinze(self):
        veredito = business_rules.aplicar(
            95.0, 0.9, Contexto(dominio_impostor=True, veiculo_imitado="g1")
        )

        assert veredito.veracidade <= 15.0
        assert veredito.regra_aplicada == "RN-02"
        assert "impostor" in veredito.motivo_regra

    def test_nao_levanta_score_ja_baixo(self):
        """O teto é limite superior, não atribuição: 5 continua 5."""
        veredito = business_rules.aplicar(5.0, 0.9, Contexto(dominio_impostor=True))

        assert veredito.veracidade == 5.0


class TestRN03OpiniaoESatira:
    def test_opiniao_nao_recebe_porcentagem(self):
        veredito = business_rules.aplicar(40.0, 0.8, Contexto(natureza="opiniao"))

        assert veredito.veracidade is None
        assert not veredito.exibe_porcentagem
        assert veredito.regra_aplicada == "RN-03"

    def test_satira_nao_recebe_porcentagem(self):
        veredito = business_rules.aplicar(10.0, 0.8, Contexto(natureza="satira"))

        assert veredito.veracidade is None
        assert "sátira" in veredito.motivo_regra

    def test_tem_precedencia_sobre_tudo(self):
        """Uma coluna de opinião num domínio impostor continua sendo opinião."""
        veredito = business_rules.aplicar(
            50.0,
            0.2,
            Contexto(natureza="opiniao", dominio_impostor=True, pipeline_encerrado=True),
        )

        assert veredito.regra_aplicada == "RN-03"


class TestRN04Inconclusivo:
    def test_confianca_baixa_no_fim_vira_inconclusivo(self):
        veredito = business_rules.aplicar(
            80.0, 0.3, Contexto(pipeline_encerrado=True)
        )

        assert veredito.faixa is Faixa.INCONCLUSIVA
        assert not veredito.exibe_porcentagem
        assert veredito.regra_aplicada == "RN-04"

    def test_nao_vale_no_meio_do_pipeline(self):
        """Durante a corrida a cobertura é baixa por construção; não é inconclusivo."""
        veredito = business_rules.aplicar(
            80.0, 0.3, Contexto(pipeline_encerrado=False)
        )

        assert veredito.regra_aplicada is None

    def test_sem_nenhum_sinal_medido_e_inconclusivo(self):
        veredito = business_rules.aplicar(None, 0.0, Contexto(pipeline_encerrado=True))

        assert veredito.veracidade is None
        assert veredito.faixa is Faixa.INCONCLUSIVA
