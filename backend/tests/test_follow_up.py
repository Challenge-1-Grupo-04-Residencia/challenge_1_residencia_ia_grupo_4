"""Testes das perguntas de acompanhamento (RF-04)."""

import pytest

from src.core.engine.follow_up import Assunto, identificar_assunto, responder
from src.core.entities.checagem_registrada import ChecagemRegistrada
from src.core.entities.claim import DocumentoRelacionado
from src.core.entities.signal import medir


def checagem(**campos):
    padrao = dict(
        id="abc",
        trecho="Uma notícia qualquer",
        veracidade=30.0,
        faixa="Duvidosa",
        confianca=0.4,
        camada_parada="N3",
    )
    padrao.update(campos)
    return ChecagemRegistrada(**padrao)


class TestIdentificacaoDeAssunto:
    @pytest.mark.parametrize(
        ("pergunta", "assunto"),
        [
            ("Por que você acha isso?", Assunto.MOTIVO),
            ("porque chegou nessa nota", Assunto.MOTIVO),
            ("Quais fontes você conferiu?", Assunto.FONTES),
            ("quem publicou isso?", Assunto.FONTES),
            ("O texto é sensacionalista?", Assunto.ESTILO),
            ("como foi escrito?", Assunto.ESTILO),
            ("Você tem certeza disso?", Assunto.CONFIANCA),
            ("qual a sua confiança?", Assunto.CONFIANCA),
            ("O que faltou apurar?", Assunto.LACUNAS),
            ("o que você não conseguiu ver?", Assunto.LACUNAS),
        ],
    )
    def test_reconhece_os_temas(self, pergunta, assunto):
        assert identificar_assunto(pergunta) is assunto

    def test_pergunta_fora_dos_temas_cai_em_geral(self):
        assert identificar_assunto("qual seu time de futebol?") is Assunto.GERAL

    def test_assunto_especifico_vence_o_generico(self):
        """"Por que" está na pergunta, mas o tema real é fontes."""
        assert identificar_assunto("Por que essas fontes?") is Assunto.FONTES


def publicacao(fonte: str, titulo: str, confiavel: bool = True):
    return DocumentoRelacionado(
        titulo=titulo,
        url=f"https://news.google.com/rss/articles/{fonte}",
        fonte=fonte,
        similaridade=0.8,
        fonte_confiavel=confiavel,
    )


class TestSobreFontes:
    def test_lista_as_fontes_conferidas(self):
        r = responder(
            "quais fontes?",
            checagem(
                fontes_citadas=["https://a", "https://b"],
                documentos_relacionados=[
                    publicacao("g1.globo.com", "Matéria do G1 sobre o assunto"),
                    publicacao("folha.uol.com.br", "Matéria da Folha"),
                ],
            ),
        )

        assert r.assunto is Assunto.FONTES
        assert len(r.fontes) == 2
        assert "2" in r.texto

    def test_fonte_citada_diz_quem_publicou(self):
        """RN-05 pede que o usuário possa conferir, e para isso precisa saber de quem é.

        O buscador devolve link de redirecionador: uma lista de endereços opacos de 500
        caracteres de ``news.google.com/rss/articles/CBMijwJB...`` não permite a ninguém
        ver quem publicou.
        """
        r = responder(
            "quais fontes?",
            checagem(
                fontes_citadas=["https://a"],
                documentos_relacionados=[
                    publicacao("g1.globo.com", "Matéria do G1 sobre o assunto")
                ],
            ),
        )

        assert r.fontes[0].veiculo == "g1.globo.com"
        assert r.fontes[0].titulo == "Matéria do G1 sobre o assunto"
        assert r.fontes[0].confiavel is True

    def test_sem_fontes_explica_sem_acusar(self):
        """Ausência de corroboração não é prova de falsidade — a fala reflete isso."""
        r = responder("quais fontes?", checagem(fontes_citadas=[]))

        assert r.fontes == []
        assert "não quer dizer que seja mentira" in r.texto.lower()


class TestSobreEstilo:
    def test_usa_as_justificativas_dos_sinais_de_conteudo(self):
        r = responder(
            "como foi escrito?",
            checagem(sinais=[medir("S-07", 0.2, "Índice de sensacionalismo 0.80.")]),
        )

        assert "sensacionalismo" in r.texto.lower()
        assert "S-07" in r.sinais_citados

    def test_sem_sinais_de_conteudo_admite(self):
        r = responder("como foi escrito?", checagem(sinais=[]))

        assert "não cheguei a analisar" in r.texto.lower()


class TestSobreConfianca:
    def test_informa_quanto_foi_medido(self):
        r = responder(
            "tem certeza?",
            checagem(sinais=[medir("S-01", 1.0), medir("S-11", None)]),
        )

        assert "12 de 100" in r.texto
        assert "faltaram 1" in r.texto.lower()


class TestSobreLacunas:
    def test_nomeia_os_sinais_indisponiveis(self):
        r = responder(
            "o que faltou?",
            checagem(sinais=[medir("S-11", None), medir("S-01", 1.0)]),
        )

        assert "veículos confiáveis" in r.texto.lower()
        assert "S-11" in r.sinais_citados

    def test_explica_que_sinal_ausente_nao_conta_contra(self):
        """RN-06 dito em linguagem de usuário."""
        r = responder("o que faltou?", checagem(sinais=[medir("S-11", None)]))

        assert "não conto como ponto contra" in r.texto.lower()

    def test_sem_lacunas_diz_que_apurou_tudo(self):
        r = responder("o que faltou?", checagem(sinais=[medir("S-01", 1.0)]))

        assert "tudo" in r.texto.lower()


class TestSobreMotivo:
    def test_regra_de_negocio_aplicada_prevalece(self):
        """Se RN-01 decidiu, o motivo é a agência, não a média dos sinais."""
        r = responder(
            "por quê?",
            checagem(
                regra_aplicada="RN-01",
                explicacao="Agência Lupa já desmentiu esta alegação.",
            ),
        )

        assert "Lupa" in r.texto

    def test_sem_regra_usa_os_principais_sinais(self):
        r = responder(
            "por quê?",
            checagem(sinais=[medir("S-06", 0.05, "Estilo muito apelativo.")]),
        )

        assert "apelativo" in r.texto.lower()
        assert "S-06" in r.sinais_citados

    def test_sem_nada_apurado_admite(self):
        r = responder("por quê?", checagem(sinais=[]))

        assert "não consegui apurar" in r.texto.lower()


class TestRespostaGeral:
    def test_admite_o_limite_em_vez_de_inventar(self):
        """Fabricar resposta seria pior do que dizer o alcance."""
        r = responder("qual seu time?", checagem(veracidade=30.0))

        assert "ainda não sei responder" in r.texto.lower()
        assert "30%" in r.texto

    def test_sem_porcentagem_nao_mostra_numero(self):
        """RN-03: opinião e sátira não recebem porcentagem, nem no acompanhamento."""
        r = responder(
            "qual seu time?",
            checagem(veracidade=None, exibe_porcentagem=False, faixa="Inconclusiva"),
        )

        assert "%" not in r.texto
