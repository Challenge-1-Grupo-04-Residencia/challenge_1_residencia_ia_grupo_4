"""Testes do adaptador do GDELT (RF-27).

Nenhum toca a rede: o cliente HTTP é injetado. A medição de 05/10 encontrou esta camada
**morta em silêncio** — timeout de 8 s contra uma API que responde em 15 a 23 s, limite
de uma consulta a cada 5 s devolvendo HTTP 429, e um ``except`` que convertia tudo em
lista vazia sem log. A N3 lia a lista vazia como "ninguém publicou", e a dimensão
Corroboração, que vale 40 dos 100 pontos, nunca era medida.
"""

import httpx
import pytest

from src.core.ports.news_search import BuscaIndisponivel
from src.infrastructure.search.gdelt import (
    DESCANSO_DO_DISJUNTOR,
    FALHAS_PARA_ABRIR,
    MAXIMO_DE_TERMOS,
    TIMEOUT_PADRAO,
    BuscadorGdelt,
    _Disjuntor,
    termos_de_busca,
)


class _MarcapassoFalso:
    """Não espera: o teste não paga os 5,5 s do intervalo real."""

    def __init__(self):
        self.esperas = 0

    def aguardar(self) -> None:
        self.esperas += 1


def _buscador(resposta_ou_erro, marcapasso=None, disjuntor=None) -> BuscadorGdelt:
    class ClienteFalso:
        def get(self, url, params=None):
            if isinstance(resposta_ou_erro, Exception):
                raise resposta_ou_erro
            return resposta_ou_erro

    # Disjuntor novo por buscador: o de produção é global de propósito, porque o
    # GDELT fora do ar está fora para todo mundo. Em teste isso faria um caso
    # vazar no seguinte — era o que acontecia antes desta injeção.
    return BuscadorGdelt(
        cliente=ClienteFalso(),
        marcapasso=marcapasso or _MarcapassoFalso(),
        disjuntor=disjuntor or _Disjuntor(FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR),
    )


def _resposta(status: int, corpo: str, json_valido: bool = True) -> httpx.Response:
    return httpx.Response(
        status_code=status,
        text=corpo,
        headers={"content-type": "application/json" if json_valido else "text/plain"},
        request=httpx.Request("GET", "https://exemplo"),
    )


class TestTermosDeBusca:
    def test_limita_os_termos(self):
        """Espaço é ``AND`` no GDELT: oito termos viravam a conjunção de oito palavras.

        A única consulta de oito termos que respondeu 200 na medição devolveu ``{}``.
        """
        texto = " ".join(f"palavra{i}" for i in range(20))

        assert len(termos_de_busca(texto).split()) <= MAXIMO_DE_TERMOS

    def test_texto_so_com_stopwords_devolve_vazio(self):
        assert termos_de_busca("a de do que e para com") == ""


class TestFalhasViramIndisponibilidade:
    def test_limite_de_uso_levanta_indisponivel(self):
        """HTTP 429 é o que o plano gratuito devolve para consultas em sequência."""
        buscador = _buscador(
            _resposta(429, "Please limit requests to one every 5 seconds", False)
        )

        with pytest.raises(BuscaIndisponivel, match="limite de uso"):
            buscador.buscar("notícia sobre vacinação nacional")

    def test_timeout_levanta_indisponivel(self):
        buscador = _buscador(httpx.ConnectTimeout("estourou"))

        with pytest.raises(BuscaIndisponivel, match="não respondeu"):
            buscador.buscar("notícia sobre vacinação nacional")

    def test_falha_de_rede_levanta_indisponivel(self):
        buscador = _buscador(httpx.ConnectError("sem rede"))

        with pytest.raises(BuscaIndisponivel):
            buscador.buscar("notícia sobre vacinação nacional")

    def test_erro_do_servidor_levanta_indisponivel(self):
        buscador = _buscador(_resposta(503, "indisponível", False))

        with pytest.raises(BuscaIndisponivel, match="HTTP 503"):
            buscador.buscar("notícia sobre vacinação nacional")

    def test_corpo_nao_json_com_status_200_levanta_indisponivel(self):
        """O GDELT sinaliza alguns erros com 200 e corpo em texto puro."""
        buscador = _buscador(_resposta(200, "Please contact the maintainer", False))

        with pytest.raises(BuscaIndisponivel, match="não-JSON"):
            buscador.buscar("notícia sobre vacinação nacional")

    def test_falha_nunca_devolve_lista_vazia(self):
        """A regressão que matou a camada: lista vazia vira "ninguém publicou" na N3.

        Confundir falha com ausência de publicação é a confusão que RN-06 proíbe, e sem
        exceção nem log a camada ficava no chão sem ninguém perceber.
        """
        buscador = _buscador(httpx.ConnectTimeout("estourou"))

        with pytest.raises(BuscaIndisponivel):
            resultado = buscador.buscar("notícia sobre vacinação nacional")
            assert resultado != []


class TestSucesso:
    def test_resposta_vazia_e_lista_vazia_e_nao_erro(self):
        """Busca que funcionou e não achou nada é informação legítima."""
        buscador = _buscador(_resposta(200, '{"articles": []}'))

        assert buscador.buscar("notícia sobre vacinação nacional") == []

    def test_converte_artigos_e_marca_veiculo_confiavel(self):
        corpo = (
            '{"articles": ['
            '{"title": "Primeira", "url": "https://g1.globo.com/a", '
            '"domain": "g1.globo.com", "seendate": "20261005T000000Z"},'
            '{"title": "Segunda", "url": "https://blogfuleiro.net/b", '
            '"domain": "blogfuleiro.net"}'
            "]}"
        )
        documentos = _buscador(_resposta(200, corpo)).buscar("vacinação nacional")

        assert len(documentos) == 2
        assert documentos[0].fonte == "g1.globo.com"
        assert documentos[0].fonte_confiavel is True
        assert documentos[1].fonte_confiavel is False
        # Similaridade derivada da posição: o primeiro é o mais relevante.
        assert documentos[0].similaridade > documentos[1].similaridade

    def test_artigo_sem_titulo_nao_quebra(self):
        corpo = '{"articles": [{"url": "https://g1.globo.com/a", "domain": "g1.globo.com"}]}'

        documentos = _buscador(_resposta(200, corpo)).buscar("vacinação nacional")

        assert documentos[0].titulo == ""


class TestRitmoETempo:
    def test_espera_o_intervalo_antes_de_chamar(self):
        """Sem espaçar as chamadas, duas requisições simultâneas tomam 429 juntas."""
        marcapasso = _MarcapassoFalso()
        _buscador(_resposta(200, '{"articles": []}'), marcapasso).buscar(
            "vacinação nacional"
        )

        assert marcapasso.esperas == 1

    def test_timeout_padrao_cobre_a_latencia_real_da_api(self):
        """Latência medida: 15 a 23 s. Um timeout de 8 s falhava sempre."""
        assert TIMEOUT_PADRAO >= 25.0


class TestDisjuntor:
    """Com o GDELT fora, insistir custa o timeout inteiro em cada checagem.

    Na medição o serviço falhava em 100% das consultas: sem disjuntor, todo usuário
    esperava 25 s para chegar à mesma conclusão da checagem anterior. Insistir também é
    o que mantém o 429 vindo de uma API que acabou de pedir para desacelerar.
    """

    def test_abre_depois_de_falhas_seguidas_e_nao_chama_mais(self):
        class ClienteQueConta:
            def __init__(self):
                self.chamadas = 0

            def get(self, url, params=None):
                self.chamadas += 1
                raise httpx.ConnectTimeout("estourou")

        cliente = ClienteQueConta()
        buscador = BuscadorGdelt(
            cliente=cliente,
            marcapasso=_MarcapassoFalso(),
            disjuntor=_Disjuntor(FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR),
        )

        for _ in range(FALHAS_PARA_ABRIR + 4):
            with pytest.raises(BuscaIndisponivel):
                buscador.buscar("notícia sobre vacinação nacional")

        # Depois de abrir, nenhuma chamada nova sai.
        assert cliente.chamadas == FALHAS_PARA_ABRIR

    def test_disjuntor_aberto_falha_na_hora(self):
        disjuntor = _Disjuntor(FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR)
        buscador = _buscador(httpx.ConnectTimeout("estourou"), disjuntor=disjuntor)
        for _ in range(FALHAS_PARA_ABRIR):
            with pytest.raises(BuscaIndisponivel):
                buscador.buscar("notícia sobre vacinação nacional")

        with pytest.raises(BuscaIndisponivel, match="parei de tentar"):
            buscador.buscar("outra notícia sobre vacinação nacional")

    def test_sucesso_fecha_o_disjuntor(self):
        disjuntor = _Disjuntor(FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR)
        falhando = _buscador(httpx.ConnectTimeout("estourou"), disjuntor=disjuntor)
        for _ in range(FALHAS_PARA_ABRIR - 1):
            with pytest.raises(BuscaIndisponivel):
                falhando.buscar("notícia sobre vacinação nacional")

        funcionando = _buscador(_resposta(200, '{"articles": []}'), disjuntor=disjuntor)
        assert funcionando.buscar("notícia sobre vacinação nacional") == []

        # Zerado: faltam FALHAS_PARA_ABRIR novas falhas para abrir de novo.
        for _ in range(FALHAS_PARA_ABRIR - 1):
            with pytest.raises(BuscaIndisponivel):
                falhando.buscar("notícia sobre vacinação nacional")
        assert funcionando.buscar("notícia sobre vacinação nacional") == []

    def test_depois_do_descanso_deixa_sondar_de_novo(self):
        """O disjuntor não pode fechar a camada para sempre — o serviço pode voltar."""
        disjuntor = _Disjuntor(FALHAS_PARA_ABRIR, descanso=0.0)
        buscador = _buscador(httpx.ConnectTimeout("estourou"), disjuntor=disjuntor)
        for _ in range(FALHAS_PARA_ABRIR):
            with pytest.raises(BuscaIndisponivel):
                buscador.buscar("notícia sobre vacinação nacional")

        # Com descanso zero, a próxima já passa pela rede: a mensagem é a do timeout,
        # não a do disjuntor.
        with pytest.raises(BuscaIndisponivel, match="não respondeu"):
            buscador.buscar("notícia sobre vacinação nacional")

    def test_consulta_vazia_nao_conta_como_falha(self):
        """Texto só com stopwords não é falha do provedor."""
        disjuntor = _Disjuntor(FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR)
        buscador = _buscador(_resposta(200, '{"articles": []}'), disjuntor=disjuntor)

        for _ in range(FALHAS_PARA_ABRIR + 2):
            assert buscador.buscar("a de do que e para com") == []

        assert buscador.buscar("notícia sobre vacinação nacional") == []
