"""Testes da leitura de checagens já publicadas por agências (RF-17, RN-01).

Os títulos usados aqui são reais, colhidos dos feeds do G1 Fato ou Fake e do Aos Fatos
em 05/10/2026 — o formato do veredito no título é o que este módulo depende, então vale
testar contra o formato de verdade e não contra um inventado.
"""

import pytest

from src.core.engine import checagens_publicadas as cp


class TestVereditoNoTitulo:
    @pytest.mark.parametrize(
        "titulo",
        [
            "É #FAKE que Lula jogou bandeira do Brasil no chão após votar",
            "É #Fake que a urna foi fraudada",
            "É falso que Gilmar Mendes entrou na cabine de votação com celular",
            "É mentira que o governo vai taxar o Pix",
            "É boato que a vacina contém grafeno",
            "Ao contrário do que apontam montagens, Lula não jogou a bandeira no chão",
        ],
    )
    def test_reconhece_veredito_falso(self, titulo):
        assert cp.veredito_no_titulo(titulo) == "falso"

    @pytest.mark.parametrize(
        "titulo",
        [
            "É #FATO: problema na rede elétrica atrasou funcionamento de urna",
            "É verdade que o prazo de inscrição foi prorrogado",
        ],
    )
    def test_reconhece_veredito_verdadeiro(self, titulo):
        assert cp.veredito_no_titulo(titulo) == "verdadeiro"

    def test_negacao_nao_inverte_o_veredito(self):
        """"não é verdade que" contém "é verdade que".

        Ler o segundo inverteria o veredito da checagem — o erro mais caro que este
        módulo pode cometer, porque RN-01 manda o score para 90 sem apelação.
        """
        assert cp.veredito_no_titulo("Não é verdade que a urna foi fraudada") == "falso"

    @pytest.mark.parametrize(
        "titulo",
        [
            "Desemprego cai a 5,3% e número de ocupados bate recorde",
            "Resultado das eleições 2026 para governador em Aracaju",
            "Entrega de colas em branco por mesários não configura irregularidade",
            "",
        ],
    )
    def test_titulo_sem_formula_de_veredito_devolve_nada(self, titulo):
        assert cp.veredito_no_titulo(titulo) is None


class TestTravaDeAlegacao:
    CHECAGEM = "É #FAKE que Lula jogou bandeira do Brasil no chão após votar"

    def test_aceita_quando_fala_do_mesmo_fato(self):
        pergunta = (
            "vi um vídeo do Lula jogando a bandeira do Brasil no chão depois de votar, "
            "isso procede?"
        )

        assert cp.trata_da_mesma_alegacao(self.CHECAGEM, pergunta)

    def test_recusa_quando_so_cita_a_mesma_pessoa(self):
        """O veredito de uma checagem não pode decidir outra alegação.

        Esta é a trava que separa "a agência checou isto" de "a agência escreveu sobre
        alguém mencionado nisto".
        """
        pergunta = "qual foi o resultado da eleição para governador em Aracaju?"

        assert not cp.trata_da_mesma_alegacao(self.CHECAGEM, pergunta)

    def test_recusa_com_poucas_palavras_em_comum(self):
        """Fração alta sobre duas palavras não significa nada."""
        assert not cp.trata_da_mesma_alegacao("É falso que Lula votou", "Lula votou")


class TestEncontrar:
    PUBLICACOES = [
        ("poder360.com.br", "Eleições 2026: veja a apuração em tempo real"),
        ("g1.globo.com", "É #FAKE que Lula jogou bandeira do Brasil no chão após votar"),
        ("aosfatos.org", "É falso que pesquisa mostra Flávio com 61% das intenções"),
    ]

    def test_acha_a_checagem_entre_publicacoes_comuns(self):
        achado = cp.encontrar(
            "o Lula jogou a bandeira do Brasil no chão depois de votar?",
            self.PUBLICACOES,
        )

        assert achado is not None
        assert achado.veredito == "falso"
        assert achado.agencia == "g1.globo.com"

    def test_ignora_checagem_de_outra_alegacao(self):
        achado = cp.encontrar(
            "quando sai o resultado da apuração das eleições?", self.PUBLICACOES
        )

        assert achado is None

    def test_sem_checagem_nenhuma_devolve_nada(self):
        achado = cp.encontrar(
            "o Lula jogou a bandeira do Brasil no chão?",
            [("poder360.com.br", "Eleições 2026: veja a apuração em tempo real")],
        )

        assert achado is None

    def test_titulo_vazio_nao_quebra(self):
        assert cp.encontrar("qualquer texto aqui", [("g1.globo.com", "")]) is None
