"""Adaptador da GDELT Doc 2.0 API para busca de notícias semelhantes (RF-27).

O GDELT indexa notícias do mundo todo em tempo quase real e não exige chave de API, o
que o torna a fonte de corroboração mais barata disponível para a N3.

A API casa por **palavra-chave**, não por similaridade semântica: este adaptador extrai
os termos mais distintivos do texto e usa a posição no ranking do próprio GDELT como
aproximação de similaridade. Quando o corpus local por embeddings estiver pronto, o
ideal é reordenar estes resultados por similaridade real.

## O que a medição de 05/10 mostrou, e o que mudou aqui

A camada estava **morta em produção, em silêncio**. Três causas somadas:

1. **Timeout menor que a latência da API.** O orçamento de 8 s da N3 virou
   ``timeout=8``, e o GDELT responde em 15 a 23 s. Toda busca estourava.
2. **Limite de uso.** O serviço gratuito responde ``HTTP 429`` com corpo em texto puro
   ("limit requests to one every 5 seconds") para quem consulta em sequência.
3. **Consulta restritiva demais.** Espaço é ``AND`` no GDELT, então oito termos
   viravam a conjunção de oito palavras: a única consulta que respondeu 200 devolveu
   ``{}``.

E o ``except`` devolvia lista vazia para tudo isso, sem log, o que a N3 lia como
"ninguém publicou". Resultado: a dimensão Corroboração — 40 dos 100 pontos do catálogo —
nunca era medida, e cada checagem gastava 8 s esperando um erro.

Mudou: o timeout passou a cobrir a latência real, as chamadas são espaçadas para não
tomar 429, a consulta usa menos termos, e qualquer falha levanta
:class:`BuscaIndisponivel` com log em vez de sumir.

Com o serviço fora do ar, um disjuntor para de tentar depois de três falhas seguidas:
sem ele, **toda** checagem pagava o timeout inteiro — 25 s de espera para chegar à mesma
conclusão da checagem anterior.

!!! warning "Isto não fecha o orçamento de latência"
    Mesmo consertado, o plano gratuito do GDELT custa de 15 a 25 s por consulta e
    aceita uma chamada a cada 5 s. É incompatível com a meta de latência da N3 e com
    mais de um usuário simultâneo. O conserto aqui tira a camada do chão; a decisão de
    produto — contratar um provedor de busca ou montar o índice próprio — continua
    aberta e é do PO.
"""

import logging
import re
import time

import httpx

from src.core.engine.text_style import VOCABULARIO_DE_URGENCIA
from src.core.entities.claim import DocumentoRelacionado
from src.core.ports.news_search import BuscaIndisponivel
from src.infrastructure.search.resiliencia import Disjuntor, Marcapasso
from src.infrastructure.search.tfidf_search import STOPWORDS_PT
from src.infrastructure.sources import veiculos

_log = logging.getLogger(__name__)

URL_API = "https://api.gdeltproject.org/api/v2/doc/doc"

_PALAVRA = re.compile(r"\b[\wÀ-ÿ]{4,}\b", re.UNICODE)

#: Às stopwords da língua somam-se os termos de urgência: "urgente", "repassem" e
#: "compartilhem" descrevem a embalagem da mensagem, não o assunto, e tomavam as vagas
#: da consulta justamente nos textos sensacionalistas — que são os que mais precisam de
#: corroboração. Ver ``VOCABULARIO_DE_URGENCIA``.
_STOPWORDS = frozenset(STOPWORDS_PT) | {
    palavra
    for termo in VOCABULARIO_DE_URGENCIA
    for palavra in termo.split()
}

#: Espaço é ``AND`` no GDELT: cada termo a mais restringe o resultado. Quatro termos é o
#: ponto em que a consulta ainda identifica o assunto sem exigir a frase inteira.
MAXIMO_DE_TERMOS = 4

#: A API gratuita pede uma chamada a cada 5 s e responde 429 para quem insiste. Um
#: pouco de folga evita bater exatamente na borda.
INTERVALO_MINIMO_ENTRE_CHAMADAS = 5.5

#: Latência medida do serviço: 15 a 23 s. Um timeout menor que isso falha sempre.
TIMEOUT_PADRAO = 25.0

#: Falhas seguidas antes de o disjuntor abrir e a camada parar de tentar.
FALHAS_PARA_ABRIR = 3

#: Quanto o disjuntor fica aberto antes de deixar uma tentativa passar.
DESCANSO_DO_DISJUNTOR = 120.0


def termos_de_busca(texto: str, maximo: int = MAXIMO_DE_TERMOS) -> str:
    """Reduz o texto a poucas palavras distintivas para consultar a API.

    Mandar o texto inteiro faz o GDELT não devolver nada: a consulta vira um ``AND``
    longo demais. Frequência simples basta porque as palavras funcionais já saíram
    pelas stopwords.
    """
    palavras = [
        p.lower() for p in _PALAVRA.findall(texto) if p.lower() not in _STOPWORDS
    ]
    if not palavras:
        return ""
    frequencia: dict[str, int] = {}
    for palavra in palavras:
        frequencia[palavra] = frequencia.get(palavra, 0) + 1
    # Desempata pela ordem de aparição, que tende a colocar o assunto principal antes.
    ordem = {p: i for i, p in enumerate(dict.fromkeys(palavras))}
    melhores = sorted(frequencia, key=lambda p: (-frequencia[p], ordem[p]))[:maximo]
    return " ".join(melhores)


#: Compartilhados por todas as instâncias: os limites do GDELT são por IP, não por
#: objeto, e o serviço fora do ar está fora para todo mundo.
_marcapasso = Marcapasso(INTERVALO_MINIMO_ENTRE_CHAMADAS)
_disjuntor = Disjuntor("GDELT", FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR)


class BuscadorGdelt:
    """Busca notícias semelhantes na GDELT Doc 2.0 API."""

    def __init__(
        self,
        idioma: str = "portuguese",
        timeout: float = TIMEOUT_PADRAO,
        cliente: httpx.Client | None = None,
        marcapasso: Marcapasso | None = None,
        disjuntor: Disjuntor | None = None,
    ):
        self.idioma = idioma
        self.timeout = timeout
        self._cliente = cliente
        # Injetáveis para o teste não esperar 5,5 s de verdade nem herdar o estado
        # de falha de outro teste.
        self._marcapasso = marcapasso if marcapasso is not None else _marcapasso
        self._disjuntor = disjuntor if disjuntor is not None else _disjuntor

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        """Top-k notícias relacionadas.

        Levanta :class:`BuscaIndisponivel` se a busca não pôde ser feita. Devolve lista
        vazia só quando a API respondeu e não havia nada — a N3 precisa dessa diferença
        para não dizer "ninguém publicou" quando o que houve foi uma falha nossa.
        """
        consulta = termos_de_busca(texto)
        if not consulta:
            return []

        if self._disjuntor.aberto():
            raise BuscaIndisponivel(
                "a busca está fora do ar; parei de tentar por alguns minutos"
            )

        parametros = {
            "query": f"{consulta} sourcelang:{self.idioma}",
            "mode": "artlist",
            "format": "json",
            "maxrecords": str(max(1, min(top_k, 50))),
            "sort": "hybridrel",
        }

        try:
            artigos, decorrido = self._consultar(parametros)
        except BuscaIndisponivel:
            self._disjuntor.registrar_falha()
            raise

        self._disjuntor.registrar_sucesso()
        _log.info(
            "GDELT: %d artigos para %r em %.1fs", len(artigos), consulta, decorrido
        )
        return [
            self._converter(artigo, posicao, len(artigos))
            for posicao, artigo in enumerate(artigos)
        ]

    def _consultar(self, parametros: dict) -> tuple[list, float]:
        """Faz a consulta e devolve os artigos, ou levanta :class:`BuscaIndisponivel`."""
        self._marcapasso.aguardar()
        inicio = time.monotonic()
        try:
            resposta = self._requisitar(parametros)
        except httpx.TimeoutException as erro:
            raise BuscaIndisponivel(
                f"GDELT não respondeu em {self.timeout:.0f}s"
            ) from erro
        except httpx.HTTPError as erro:
            raise BuscaIndisponivel(
                f"falha de rede ao consultar o GDELT: {erro}"
            ) from erro

        decorrido = time.monotonic() - inicio

        if resposta.status_code == 429:
            raise BuscaIndisponivel(
                "limite de uso do GDELT estourado (1 consulta a cada 5s)"
            )
        if resposta.status_code >= 400:
            raise BuscaIndisponivel(f"GDELT devolveu HTTP {resposta.status_code}")

        try:
            artigos = resposta.json().get("articles", [])
        except ValueError as erro:
            # 200 com corpo em texto puro é como o GDELT sinaliza alguns erros.
            raise BuscaIndisponivel(
                f"GDELT devolveu corpo não-JSON: {resposta.text[:80]!r}"
            ) from erro

        if not isinstance(artigos, list):
            raise BuscaIndisponivel("campo 'articles' do GDELT não é uma lista")

        return artigos, decorrido

    def _requisitar(self, parametros: dict) -> httpx.Response:
        if self._cliente is not None:
            return self._cliente.get(URL_API, params=parametros)
        with httpx.Client(timeout=self.timeout) as cliente:
            return cliente.get(URL_API, params=parametros)

    @staticmethod
    def _converter(artigo: dict, posicao: int, total: int) -> DocumentoRelacionado:
        """Traduz um artigo do GDELT, derivando similaridade da posição no ranking.

        A API não expõe o score de relevância, então a posição é o único sinal de
        proximidade disponível: o primeiro resultado recebe 1,0 e os seguintes decaem
        linearmente. É uma aproximação, e está marcada como tal na documentação da N3.
        """
        url = artigo.get("url")
        similaridade = 1.0 - (posicao / total) if total > 1 else 1.0
        return DocumentoRelacionado(
            titulo=(artigo.get("title") or "").strip(),
            url=url,
            fonte=artigo.get("domain", "") or (veiculos.normalizar_dominio(url) or ""),
            similaridade=round(max(0.0, min(1.0, similaridade)), 4),
            # Posição no ranking não é comparação de texto: S-13 não pode usá-la como
            # medida de cópia. Ver ``DocumentoRelacionado.similaridade_textual``.
            similaridade_textual=False,
            fonte_confiavel=veiculos.e_confiavel(url or artigo.get("domain")),
            data_publicacao=artigo.get("seendate"),
        )
