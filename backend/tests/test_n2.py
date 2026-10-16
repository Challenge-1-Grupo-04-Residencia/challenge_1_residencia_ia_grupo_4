"""Testes da camada N2 · Conteúdo (RF-21, RF-22, RF-24)."""

import pytest

from src.core.engine import text_style
from src.core.engine.n2_content import CamadaN2Conteudo
from src.core.entities.claim import NoticiaRequest

TEXTO_SENSACIONALISTA = (
    "URGENTE!!! REPASSEM PARA TODOS!!! O governo quer matar a população com as novas "
    "vacinas que contêm chip!!! Acordem povo brasileiro!!! Cuidado!!!"
)
TEXTO_JORNALISTICO = (
    "Nesta terça-feira, o Ministério da Saúde anunciou uma nova campanha de vacinação "
    "nacional contra o vírus da gripe. A medida visa proteger a população."
)


@pytest.fixture
def camada_n2():
    return CamadaN2Conteudo()


def sinal(resultado, id_sinal: str):
    return next(s for s in resultado.sinais if s.id == id_sinal)


class TestIndiceDeSensacionalismo:
    """Heurística pura, testável sem carregar o modelo de ML."""

    def test_texto_sobrio_nao_tem_o_que_medir(self):
        """Ausência de marca é ``None``, não zero: a diferença é RN-06.

        Zero virava score 1,0 na camada e somava veracidade a qualquer texto que não
        gritasse — o que fazia mentira em tom sóbrio pontuar alto.
        """
        assert text_style.indice_sensacionalismo(TEXTO_JORNALISTICO) is None

    def test_corrente_de_mensageiro_pontua_alto(self):
        assert text_style.indice_sensacionalismo(TEXTO_SENSACIONALISTA) > 0.4

    def test_texto_vazio_nao_quebra(self):
        assert text_style.indice_sensacionalismo("") is None

    def test_siglas_nao_contam_como_grito(self):
        """``STF`` e ``OMS`` são escrita normal, não grito.

        A caixa alta saiu do índice justamente por isto: medida nos corpora, ela
        dispara mais em notícia verdadeira (39,7%) do que em falsa (30,7%), porque
        sigla de órgão e manchete entravam como berro.
        """
        com_siglas = "O STF e a OMS divulgaram a nota técnica conjunta nesta semana."

        assert text_style.indice_sensacionalismo(com_siglas) is None

    def test_indice_fica_no_intervalo_valido(self):
        for texto in ("", TEXTO_JORNALISTICO, TEXTO_SENSACIONALISTA, "!!!" * 100):
            indice = text_style.indice_sensacionalismo(texto)
            assert indice is None or 0.0 <= indice <= 1.0

    def test_mais_marcadores_dao_indice_maior(self):
        """A medição mostrou monotonia: 1 marcador → 68% de chance de ser falsa, 2 → 76%."""
        um = text_style.indice_sensacionalismo("O preço do pão subiu de novo!!")
        varios = text_style.indice_sensacionalismo(
            "URGENTE!!! REPASSEM!!! COMPARTILHEM antes que apaguem!!!"
        )

        assert um < varios


class TestIndiceDeCitacaoDeFontes:
    def test_texto_sem_ancoragem_pontua_zero(self):
        assert text_style.indice_citacao_de_fontes("Dizem por aí que vai subir.") == 0.0

    def test_links_contam_como_citacao(self):
        texto = "Veja https://a.com/x e https://b.com/y e https://c.com/z"

        assert text_style.indice_citacao_de_fontes(texto) == 1.0

    def test_orgao_nomeado_conta_como_citacao(self):
        assert text_style.indice_citacao_de_fontes(TEXTO_JORNALISTICO) > 0.0


class TestCamadaN2:
    def test_texto_curto_deixa_s06_indisponivel(self, camada_n2):
        """Sem texto suficiente o classificador não é confiável — RN-06 em ação."""
        noticia = camada_n2.processar(
            NoticiaRequest(texto="O ministro pediu demissão nesta manhã.")
        )

        assert sinal(noticia.resultado, "S-06").score is None
        assert "Texto muito curto" in noticia.resultado.explicacao

    def test_texto_curto_deixa_todos_os_sinais_de_estilo_indisponiveis(self, camada_n2):
        """Em "Oi, tudo bem?" não há nada a medir — e nada a creditar.

        Era aqui que a Vera tratava uma saudação como notícia: S-07 e S-08 valiam 1,0
        por falta de gritaria e S-09 valia 0,0 por falta de citação, o que dava 77% de
        veracidade a um "bom dia". Nenhum dos quatro sinais deve ter leitura.
        """
        noticia = camada_n2.processar(NoticiaRequest(texto="Oi, tudo bem?"))

        for id_sinal in ("S-06", "S-07", "S-08", "S-09"):
            assert sinal(noticia.resultado, id_sinal).score is None, id_sinal
        assert noticia.resultado.cobertura == 0.0

    def test_detectores_silenciosos_ficam_indisponiveis(self, camada_n2):
        """Texto jornalístico comum não dispara S-07 nem S-08."""
        noticia = camada_n2.processar(NoticiaRequest(texto=TEXTO_JORNALISTICO))

        assert sinal(noticia.resultado, "S-07").score is None
        assert sinal(noticia.resultado, "S-08").score is None
        assert sinal(noticia.resultado, "S-09").score is not None

    def test_sensacionalismo_derruba_s07(self, camada_n2):
        noticia = camada_n2.processar(NoticiaRequest(texto=TEXTO_SENSACIONALISTA))

        assert sinal(noticia.resultado, "S-07").score < 0.5

    def test_detectores_nunca_creditam_veracidade(self, camada_n2):
        """S-07 e S-08 moram em [0; 0,5]: no máximo descontam, nunca somam.

        Com teto em 1,0 os dois somavam 10 dos 23 pontos ativos quase sempre no
        máximo, e só 11,9% a 25% das notícias falsas dos corpora chegavam à faixa
        "provavelmente falsa".
        """
        indignado = camada_n2.processar(
            NoticiaRequest(
                texto=(
                    "Esses bandidos corruptos são uns vagabundos ladrões, uma gente "
                    "podre e nojenta que merece cadeia agora mesmo!!!"
                )
            )
        )

        for id_sinal in ("S-07", "S-08"):
            score = sinal(indignado.resultado, id_sinal).score
            assert score is not None, id_sinal
            assert 0.0 <= score <= 0.5, id_sinal

    def test_emocao_nao_dispara_com_noticia_triste(self, camada_n2):
        """Jornalismo sério sobre notícia ruim não é manipulação emocional.

        "morte", "crise", "risco" e "doença" aparecem de 2 a 4 vezes mais em notícia
        **verdadeira** nos corpora. Enquanto estavam no léxico, uma matéria do
        Ministério da Saúde sobre dengue zerava S-08.
        """
        noticia = camada_n2.processar(
            NoticiaRequest(
                texto=(
                    "O Ministério da Saúde confirmou a morte de um paciente por dengue "
                    "no interior de São Paulo. Segundo a Fiocruz, o risco de novos "
                    "casos segue alto durante a crise sazonal da doença."
                )
            )
        )

        assert sinal(noticia.resultado, "S-08").score is None

    def test_camada_atual_marcada(self, camada_n2):
        noticia = camada_n2.processar(NoticiaRequest(texto=TEXTO_JORNALISTICO))

        assert noticia.resultado.camada_atual == "N2"

    def test_texto_sensacionalista_tem_veracidade_menor(self, camada_n2):  # noqa: D102
        """O score agora sai da média ponderada dos sinais, não de subtração direta."""
        suspeito = camada_n2.processar(NoticiaRequest(texto=TEXTO_SENSACIONALISTA))
        sobrio = camada_n2.processar(NoticiaRequest(texto=TEXTO_JORNALISTICO))

        assert suspeito.resultado.veracidade < sobrio.resultado.veracidade

    def test_explicacao_menciona_estilo_apelativo(self, camada_n2):
        if camada_n2.modelo is None:
            pytest.skip("Modelo de ML (.joblib) não carregado.")

        noticia = camada_n2.processar(NoticiaRequest(texto=TEXTO_SENSACIONALISTA))

        assert "estilo de escrita apelativo" in noticia.resultado.explicacao

    def test_texto_jornalistico_aprovado(self, camada_n2):
        if camada_n2.modelo is None:
            pytest.skip("Modelo de ML (.joblib) não carregado.")

        noticia = camada_n2.processar(NoticiaRequest(texto=TEXTO_JORNALISTICO))

        assert "não aparenta ser sensacionalista" in noticia.resultado.explicacao
