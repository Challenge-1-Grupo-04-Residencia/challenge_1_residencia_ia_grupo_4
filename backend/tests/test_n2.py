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

    def test_texto_sobrio_pontua_baixo(self):
        assert text_style.indice_sensacionalismo(TEXTO_JORNALISTICO) < 0.2

    def test_corrente_de_mensageiro_pontua_alto(self):
        assert text_style.indice_sensacionalismo(TEXTO_SENSACIONALISTA) > 0.4

    def test_texto_vazio_nao_quebra(self):
        assert text_style.indice_sensacionalismo("") == 0.0

    def test_siglas_nao_contam_como_caixa_alta(self):
        """``STF`` e ``OMS`` são escrita normal, não grito."""
        com_siglas = "O STF e a OMS divulgaram a nota técnica conjunta nesta semana."

        assert text_style.indice_sensacionalismo(com_siglas) < 0.15

    def test_indice_fica_no_intervalo_valido(self):
        for texto in ("", TEXTO_JORNALISTICO, TEXTO_SENSACIONALISTA, "!!!" * 100):
            assert 0.0 <= text_style.indice_sensacionalismo(texto) <= 1.0


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

    def test_sempre_mede_sensacionalismo_e_citacoes(self, camada_n2):
        """S-07 e S-09 não dependem do modelo: valem até para texto curto."""
        noticia = camada_n2.processar(NoticiaRequest(texto="Texto breve demais."))

        assert sinal(noticia.resultado, "S-07").score is not None
        assert sinal(noticia.resultado, "S-09").score is not None

    def test_sensacionalismo_derruba_s07(self, camada_n2):
        noticia = camada_n2.processar(NoticiaRequest(texto=TEXTO_SENSACIONALISTA))
        sobrio = camada_n2.processar(NoticiaRequest(texto=TEXTO_JORNALISTICO))

        assert sinal(noticia.resultado, "S-07").score < sinal(sobrio.resultado, "S-07").score

    def test_camada_atual_marcada(self, camada_n2):
        noticia = camada_n2.processar(NoticiaRequest(texto=TEXTO_JORNALISTICO))

        assert noticia.resultado.camada_atual == "N2"

    def test_texto_sensacionalista_tem_veracidade_menor(self, camada_n2):
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
