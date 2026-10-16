"""Testes do adaptador do Google Notícias (RF-27).

Nenhum toca a rede: o cliente HTTP é injetado e o feed é uma fixture.
"""

import httpx
import pytest

from src.core.ports.news_search import BuscaIndisponivel
from src.infrastructure.search.google_news import (
    DESCANSO_DO_DISJUNTOR,
    FALHAS_PARA_ABRIR,
    MAXIMO_DE_TERMOS,
    BuscadorGoogleNews,
    termos_de_busca,
)
from src.infrastructure.search.resiliencia import Disjuntor


class _MarcapassoFalso:
    def aguardar(self) -> None:
        return None


def _feed(*itens: str) -> str:
    corpo = "".join(itens)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel><title>busca</title>'
        f"{corpo}"
        "</channel></rss>"
    )


def _item(titulo: str, fonte: str, url_da_fonte: str, link: str = "https://news.google.com/x") -> str:
    return (
        "<item>"
        f"<title>{titulo}</title>"
        f"<link>{link}</link>"
        "<pubDate>Sun, 05 Oct 2026 10:00:00 GMT</pubDate>"
        f'<source url="{url_da_fonte}">{fonte}</source>'
        "</item>"
    )


def _buscador(resposta_ou_erro, disjuntor=None) -> BuscadorGoogleNews:
    class ClienteFalso:
        def get(self, url, headers=None):
            if isinstance(resposta_ou_erro, Exception):
                raise resposta_ou_erro
            return resposta_ou_erro

    return BuscadorGoogleNews(
        cliente=ClienteFalso(),
        marcapasso=_MarcapassoFalso(),
        disjuntor=disjuntor or Disjuntor("teste", FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR),
    )


def _resposta(status: int, corpo: str) -> httpx.Response:
    return httpx.Response(
        status_code=status,
        text=corpo,
        headers={"content-type": "application/rss+xml"},
        request=httpx.Request("GET", "https://news.google.com/rss/search"),
    )


class TestTermosDeBusca:
    def test_limita_os_termos(self):
        texto = " ".join(f"palavra{i}" for i in range(20))

        assert len(termos_de_busca(texto).split()) <= MAXIMO_DE_TERMOS

    def test_texto_so_com_stopwords_devolve_vazio(self):
        assert termos_de_busca("a de do que e para com") == ""

    def test_consulta_vazia_nao_chega_na_rede(self):
        """Sem termo não há o que buscar, e o provedor não precisa ser incomodado."""
        class ClienteQueExplode:
            def get(self, url, headers=None):
                raise AssertionError("não deveria ter chamado a rede")

        buscador = BuscadorGoogleNews(
            cliente=ClienteQueExplode(), marcapasso=_MarcapassoFalso()
        )

        assert buscador.buscar("a de do que e") == []


class TestConversao:
    FEED = _feed(
        _item("Desemprego cai a 5,3% - Agência Brasil", "Agência Brasil",
              "https://agenciabrasil.ebc.com.br"),
        _item("Taxa fica em 5,3% em agosto", "Folha de S.Paulo",
              "https://folha.uol.com.br"),
        _item("Veja os números do IBGE", "Blog do João",
              "https://blogdojoao.net"),
    )

    def test_extrai_titulo_fonte_e_confiabilidade(self):
        documentos = _buscador(_resposta(200, self.FEED)).buscar("ibge desemprego taxa")

        assert len(documentos) == 3
        assert documentos[0].fonte == "agenciabrasil.ebc.com.br"
        assert documentos[0].fonte_confiavel is True
        assert documentos[1].fonte_confiavel is True
        assert documentos[2].fonte_confiavel is False

    def test_dominio_vem_da_fonte_e_nao_do_link(self):
        """O ``<link>`` é redirecionador do Google.

        Usá-lo faria todo resultado parecer publicado por ``news.google.com``, e nenhum
        bateria com a base curada.
        """
        documentos = _buscador(_resposta(200, self.FEED)).buscar("ibge desemprego taxa")

        for documento in documentos:
            assert "news.google.com" not in documento.fonte

    def test_remove_o_nome_do_veiculo_repetido_no_titulo(self):
        """A evidência mandada à N4 não deve terminar sempre com " - Agência Brasil"."""
        documentos = _buscador(_resposta(200, self.FEED)).buscar("ibge desemprego taxa")

        assert documentos[0].titulo == "Desemprego cai a 5,3%"
        assert documentos[1].titulo == "Taxa fica em 5,3% em agosto"

    def test_similaridade_decai_com_a_posicao(self):
        documentos = _buscador(_resposta(200, self.FEED)).buscar("ibge desemprego taxa")

        assert documentos[0].similaridade == 1.0
        assert documentos[0].similaridade > documentos[1].similaridade
        assert documentos[1].similaridade > documentos[2].similaridade

    def test_recorta_antes_de_calcular_a_similaridade(self):
        """O feed devolve até 100 itens.

        Calcular a similaridade sobre os 100 e só depois recortar faria o segundo
        resultado valer 0,99 — e o limiar de cópia da N3 é 0,9.
        """
        feed = _feed(*[
            _item(f"Notícia {i}", "Folha de S.Paulo", "https://folha.uol.com.br")
            for i in range(100)
        ])
        documentos = _buscador(_resposta(200, feed)).buscar("ibge desemprego", top_k=5)

        assert len(documentos) == 5
        assert documentos[1].similaridade == pytest.approx(0.8)

    def test_item_sem_fonte_nao_quebra(self):
        feed = _feed("<item><title>Sem fonte</title><link>https://x/y</link></item>")

        documentos = _buscador(_resposta(200, feed)).buscar("ibge desemprego taxa")

        assert documentos[0].titulo == "Sem fonte"
        assert documentos[0].fonte_confiavel is False

    def test_feed_vazio_e_lista_vazia_e_nao_erro(self):
        """Busca que funcionou e não achou nada é informação legítima, não falha."""
        assert _buscador(_resposta(200, _feed())).buscar("ibge desemprego taxa") == []


class TestFalhas:
    def test_timeout_levanta_indisponivel(self):
        with pytest.raises(BuscaIndisponivel, match="não respondeu"):
            _buscador(httpx.ConnectTimeout("estourou")).buscar("ibge desemprego taxa")

    def test_limite_de_uso_levanta_indisponivel(self):
        with pytest.raises(BuscaIndisponivel, match="limite de uso"):
            _buscador(_resposta(429, "devagar")).buscar("ibge desemprego taxa")

    def test_erro_do_servidor_levanta_indisponivel(self):
        with pytest.raises(BuscaIndisponivel, match="HTTP 503"):
            _buscador(_resposta(503, "fora")).buscar("ibge desemprego taxa")

    def test_feed_ilegivel_levanta_indisponivel(self):
        with pytest.raises(BuscaIndisponivel, match="ilegível"):
            _buscador(_resposta(200, "<rss><channel>sem fechar")).buscar("ibge desemprego")

    def test_falha_nunca_devolve_lista_vazia(self):
        """Lista vazia vira "ninguém publicou" na N3: confundir é o que RN-06 proíbe."""
        with pytest.raises(BuscaIndisponivel):
            _buscador(httpx.ConnectError("sem rede")).buscar("ibge desemprego taxa")

    def test_disjuntor_abre_depois_de_falhas_seguidas(self):
        disjuntor = Disjuntor("teste", FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR)
        buscador = _buscador(httpx.ConnectTimeout("estourou"), disjuntor=disjuntor)
        for _ in range(FALHAS_PARA_ABRIR):
            with pytest.raises(BuscaIndisponivel):
                buscador.buscar("ibge desemprego taxa")

        with pytest.raises(BuscaIndisponivel, match="parei de tentar"):
            buscador.buscar("outro assunto qualquer aqui")
