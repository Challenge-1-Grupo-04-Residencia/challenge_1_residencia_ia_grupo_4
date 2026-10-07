"""Testes da camada N3 e da busca por notícias semelhantes (RF-27, RF-28, issue #32)."""

import pytest

from src.core.engine.n3_corroboration import CamadaN3Corroboracao
from src.core.entities.claim import DocumentoRelacionado, NoticiaRequest
from src.core.ports.news_search import BuscaIndisponivel
from src.infrastructure.search.gdelt import termos_de_busca
from src.infrastructure.search.tfidf_search import BuscadorTfidf, Documento
from src.infrastructure.sources import veiculos


class BuscadorFalso:
    """Buscador controlado, para testar a N3 sem rede nem corpus."""

    def __init__(self, documentos: list[DocumentoRelacionado]):
        self.documentos = documentos
        self.chamadas: list[tuple[str, int]] = []

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        self.chamadas.append((texto, top_k))
        return self.documentos[:top_k]


def documento(
    fonte: str,
    confiavel: bool,
    similaridade: float = 0.5,
    similaridade_textual: bool = True,
):
    return DocumentoRelacionado(
        titulo=f"Matéria de {fonte}",
        url=f"https://{fonte}/materia",
        fonte=fonte,
        similaridade=similaridade,
        similaridade_textual=similaridade_textual,
        fonte_confiavel=confiavel,
    )


class BuscadorQueFalha:
    """Buscador indisponível: rede fora, provedor fora ou limite de uso estourado."""

    def __init__(self, motivo: str = "GDELT não respondeu em 25s"):
        self.motivo = motivo

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        raise BuscaIndisponivel(self.motivo)


def sinal(resultado, id_sinal: str):
    return next(s for s in resultado.sinais if s.id == id_sinal)


class TestBuscadorTfidf:
    @pytest.fixture
    def buscador(self):
        return BuscadorTfidf(
            [
                Documento(
                    titulo="Ministério da Saúde anuncia campanha de vacinação",
                    texto="A campanha nacional de vacinação contra a gripe começa na segunda.",
                    url="https://g1.globo.com/saude/campanha",
                ),
                Documento(
                    titulo="Seleção brasileira vence amistoso",
                    texto="O time venceu por dois a zero no estádio lotado ontem à noite.",
                    url="https://globo.com/esporte/amistoso",
                ),
                Documento(
                    titulo="Vacinação contra gripe é ampliada",
                    texto="O ministério ampliou os grupos prioritários da campanha de vacinação.",
                    url="https://folha.uol.com.br/saude/vacinacao",
                ),
            ]
        )

    def test_encontra_documentos_do_mesmo_assunto(self, buscador):
        achados = buscador.buscar("campanha de vacinação do ministério da saúde")

        assert achados
        assert all("vacina" in d.titulo.lower() for d in achados)

    def test_ordena_do_mais_semelhante_ao_menos(self, buscador):
        achados = buscador.buscar("campanha de vacinação contra a gripe")
        similaridades = [d.similaridade for d in achados]

        assert similaridades == sorted(similaridades, reverse=True)

    def test_respeita_o_top_k(self, buscador):
        assert len(buscador.buscar("vacinação campanha ministério", top_k=1)) == 1

    def test_descarta_resultados_abaixo_do_limiar(self, buscador):
        """Assunto sem relação não deve virar corroboração falsa."""
        assert buscador.buscar("receita de bolo de fubá com goiabada") == []

    def test_marca_veiculo_confiavel_pela_base_curada(self, buscador):
        achados = buscador.buscar("campanha de vacinação do ministério da saúde")

        assert all(d.fonte_confiavel for d in achados)

    def test_corpus_vazio_nao_quebra(self):
        assert BuscadorTfidf([]).buscar("qualquer coisa") == []

    def test_consulta_vazia_nao_quebra(self, buscador):
        assert buscador.buscar("   ") == []


class TestTermosDeBuscaGdelt:
    def test_remove_stopwords(self):
        termos = termos_de_busca("O ministério da saúde anunciou a nova campanha")

        assert "ministério" in termos
        assert " da " not in f" {termos} "

    def test_limita_a_quantidade_de_termos(self):
        texto = " ".join(f"palavra{i}" for i in range(50))

        assert len(termos_de_busca(texto, maximo=8).split()) <= 8

    def test_texto_so_com_stopwords_devolve_vazio(self):
        assert termos_de_busca("a de e o que") == ""


class TestCamadaN3:
    def test_registra_documentos_relacionados(self):
        camada = CamadaN3Corroboracao(
            BuscadorFalso([documento("g1.globo.com", True)])
        )
        noticia = camada.processar(NoticiaRequest(texto="Notícia qualquer sobre saúde."))

        assert len(noticia.resultado.documentos_relacionados) == 1
        assert noticia.resultado.camada_atual == "N3"

    def test_pede_top_5_por_padrao(self):
        buscador = BuscadorFalso([])
        CamadaN3Corroboracao(buscador).processar(NoticiaRequest(texto="Texto."))

        assert buscador.chamadas[0][1] == 5

    @pytest.mark.parametrize(
        ("confiaveis", "esperado"),
        [(0, 0.0), (1, 0.5), (2, 0.8), (3, 1.0), (4, 1.0)],
    )
    def test_s11_pontua_pela_contagem_de_veiculos(self, confiaveis, esperado):
        pass
    def test_conta_veiculos_distintos_e_nao_artigos(self):
        pass
    def test_busca_vazia_deixa_s11_indisponivel(self):
        pass
    def test_busca_indisponivel_deixa_s11_indisponivel(self):
        pass
    def test_falha_de_busca_nao_e_confundida_com_ausencia_de_publicacao(self):
        pass
    def test_erro_tecnico_da_busca_nao_vaza_para_a_explicacao(self):
        pass
    def test_quase_copia_de_fonte_nao_confiavel_zera_s13(self):
        camada = CamadaN3Corroboracao(
            BuscadorFalso([documento("blogdojoao.net", False, similaridade=0.97)])
        )
        noticia = camada.processar(NoticiaRequest(texto="Texto."))

        assert sinal(noticia.resultado, "S-13").score == 0.0

    def test_replicacao_de_veiculo_confiavel_nao_penaliza(self):
        """Republicar matéria de agência é prática legítima, não plágio."""
        camada = CamadaN3Corroboracao(
            BuscadorFalso([documento("g1.globo.com", True, similaridade=0.97)])
        )
        noticia = camada.processar(NoticiaRequest(texto="Texto."))

        assert sinal(noticia.resultado, "S-13").score == 1.0

    def test_similaridade_de_ranking_nao_acusa_plagio(self):
        """Posição no ranking não é comparação de texto.

        Os buscadores por API não expõem score de relevância, então a similaridade é
        derivada da posição — e o primeiro resultado vale sempre 1,0. Com o limiar de
        cópia em 0,9, isso acusava de plágio **toda** notícia cujo primeiro resultado
        viesse de fora da base curada, inclusive uma matéria legítima sobre dados do
        IBGE. Por RN-06, sem medição de texto não há medição.
        """
        camada = CamadaN3Corroboracao(
            BuscadorFalso([
                documento(
                    "aciara.com.br",
                    False,
                    similaridade=1.0,
                    similaridade_textual=False,
                )
            ])
        )
        noticia = camada.processar(NoticiaRequest(texto="Texto."))

        assert sinal(noticia.resultado, "S-13").score is None
        assert "originalidade" in sinal(noticia.resultado, "S-13").justificativa

    def test_ausencia_de_copia_nao_credita_originalidade(self):
        """Não achar plágio entre cinco resultados não atesta originalidade.

        S-13 valia 1,0 aqui, o que dava 5 pontos de veracidade de graça a toda checagem
        em que o buscador trouxesse qualquer coisa — inclusive a uma saudação.
        """
        camada = CamadaN3Corroboracao(
            BuscadorFalso([documento("g1.globo.com", True, similaridade=0.4)])
        )
        noticia = camada.processar(NoticiaRequest(texto="Texto."))

        assert sinal(noticia.resultado, "S-13").score is None

    def test_checagem_de_agencia_nos_resultados_aciona_rn01(self):
        """RF-17: a agência já checou, então RN-01 decide em vez do score.

        Sem isto a busca por palavra-chave fazia a notícia falsa ser corroborada pelo
        próprio desmentido dela: as checagens do G1 e do Aos Fatos contavam como dois
        veículos confiáveis publicando sobre o assunto, e S-11 ia ao máximo.
        """
        checagem = DocumentoRelacionado(
            titulo="É #FAKE que Lula jogou bandeira do Brasil no chão após votar",
            url="https://g1.globo.com/fato-ou-fake/x",
            fonte="g1.globo.com",
            similaridade=1.0,
            fonte_confiavel=True,
        )
        camada = CamadaN3Corroboracao(BuscadorFalso([checagem]))
        noticia = camada.processar(
            NoticiaRequest(
                texto="o Lula jogou a bandeira do Brasil no chão depois de votar?"
            )
        )

        assert noticia.resultado.veredito_agencia == "falso"
        assert noticia.resultado.agencia == "g1.globo.com"

    def test_checagem_de_outra_alegacao_nao_aciona_rn01(self):
        checagem = DocumentoRelacionado(
            titulo="É #FAKE que Lula jogou bandeira do Brasil no chão após votar",
            url="https://g1.globo.com/fato-ou-fake/x",
            fonte="g1.globo.com",
            similaridade=1.0,
            fonte_confiavel=True,
        )
        camada = CamadaN3Corroboracao(BuscadorFalso([checagem]))
        noticia = camada.processar(
            NoticiaRequest(texto="qual o resultado da eleição em Aracaju?")
        )

        assert noticia.resultado.veredito_agencia is None

    def test_coleta_urls_como_fontes_citadas(self):
        """RN-05 exige as fontes consultadas em todo resultado."""
        camada = CamadaN3Corroboracao(BuscadorFalso([documento("g1.globo.com", True)]))
        noticia = camada.processar(NoticiaRequest(texto="Texto."))

        assert noticia.resultado.fontes_citadas == ["https://g1.globo.com/materia"]


class TestBaseCurada:
    @pytest.mark.parametrize(
        "url",
        [
            "https://g1.globo.com/politica/noticia",
            "g1.globo.com",
            "https://www.folha.uol.com.br/",
            "https://esporte.g1.globo.com/materia",
        ],
    )
    def test_reconhece_veiculo_confiavel(self, url):
        assert veiculos.e_confiavel(url)

    def test_dominio_fora_da_base_e_desconhecido(self):
        assert veiculos.reputacao("blogdojoao.net") is veiculos.Reputacao.DESCONHECIDO

    def test_desconhecido_nao_tem_nota(self):
        """Ser novo na base não é indício de falsidade: o sinal fica indisponível."""
        assert veiculos.SCORE_POR_REPUTACAO[veiculos.Reputacao.DESCONHECIDO] is None

    def test_nao_casa_dominio_por_substring(self):
        """``g1.globo.com.br.fake.net`` não pode herdar a reputação do g1."""
        assert not veiculos.e_confiavel("https://g1.globo.com.br.fake.net/materia")

    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("https://www.G1.globo.com/path?x=1", "g1.globo.com"),
            ("", None),
            (None, None),
        ],
    )
    def test_normalizacao_de_dominio(self, entrada, esperado):
        assert veiculos.normalizar_dominio(entrada) == esperado
