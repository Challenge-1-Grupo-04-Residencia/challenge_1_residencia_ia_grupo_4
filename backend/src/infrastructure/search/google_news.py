"""Adaptador do feed RSS de busca do Google Notícias, para a camada N3 (RF-27).

É a implementação de busca que **funciona** hoje. Medido em 05/10, lado a lado com o
GDELT, na mesma consulta:

| | GDELT Doc 2.0 | Google Notícias RSS |
| --- | --- | --- |
| Latência | 15 a 23 s | **~1 s** |
| Limite de uso | 1 consulta / 5 s, com `HTTP 429` | não esbarrou |
| Resultados em português | 0 nas consultas testadas | 46 a 100 |
| Chave de API | não precisa | não precisa |

O GDELT continua no repositório como alternativa — a porta
:class:`~src.core.ports.news_search.BuscadorDeNoticias` existe para isso —, mas com a
latência e o limite que ele tem, a dimensão Corroboração, que vale 40 dos 100 pontos do
catálogo, simplesmente não era medida em produção.

## A armadilha que esta camada não resolve sozinha

Busca por palavra-chave não distingue **"o G1 publicou este fato"** de **"o G1
desmentiu esta alegação"**. Na consulta por `vacina grafeno` os três primeiros
resultados são checagens — "É #FAKE que vacinas aprovadas contra Covid-19 contenham
óxido de grafeno", do G1 — e, para S-11, isso conta como três veículos confiáveis
falando do assunto.

Quem desfaz a armadilha é a N4: ela recebe estes títulos como evidências e julga, um por
um, se **sustentam** ou **contradizem** a alegação (S-12, peso 20, o mais pesado do
catálogo). Com a N3 morta a N4 não tinha o que ler; agora que a busca funciona, ela
passou de camada opcional a necessária — é ela que lê o "É #FAKE" e devolve
`CONTRADICTION`.

Enquanto o provedor de LLM não estiver de pé, S-12 fica indisponível por RN-06 e a
corroboração é medida só pela contagem de veículos. Isso está registrado como limite
conhecido, não como resultado confiável.

## Por que o veículo não sai do link

O ``<link>`` de cada item é um redirecionador do Google. O veículo real vem no atributo
``url`` do elemento ``<source>``, e é dele que sai o domínio consultado na base curada.
Usar o link faria todo resultado parecer publicado por ``news.google.com``.
"""

import logging
import time
import urllib.parse
from xml.etree import ElementTree

import httpx

from src.core.entities.claim import DocumentoRelacionado
from src.core.ports.news_search import BuscaIndisponivel
from src.infrastructure.search.resiliencia import Disjuntor, Marcapasso
from src.infrastructure.search.tfidf_search import STOPWORDS_PT
from src.infrastructure.sources import veiculos

_log = logging.getLogger(__name__)

URL_BUSCA = "https://news.google.com/rss/search"

#: O Google Notícias casa por relevância e tolera consulta mais longa que o GDELT, cujo
#: espaço é ``AND``. Seis termos descrevem o assunto sem virar a frase inteira.
MAXIMO_DE_TERMOS = 6

#: Não esbarramos em limite na medição, mas espaçar as chamadas é a diferença entre ser
#: um consumidor educado de um serviço gratuito e ser bloqueado mais tarde.
INTERVALO_MINIMO_ENTRE_CHAMADAS = 1.0

TIMEOUT_PADRAO = 10.0
FALHAS_PARA_ABRIR = 3
DESCANSO_DO_DISJUNTOR = 120.0

#: Sem um agente identificável alguns serviços recusam a requisição.
AGENTE = "Mozilla/5.0 (compatible; SenhoraVera/0.3; +checador de noticias)"

_marcapasso = Marcapasso(INTERVALO_MINIMO_ENTRE_CHAMADAS)
_disjuntor = Disjuntor("Google Notícias", FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR)

_STOPWORDS = frozenset(STOPWORDS_PT)


def termos_de_busca(texto: str, maximo: int = MAXIMO_DE_TERMOS) -> str:
    """Reduz o texto aos termos mais distintivos, para a consulta descrever o assunto.

    Reaproveita a regra do adaptador do GDELT: palavras de quatro letras ou mais, sem
    stopwords, ordenadas por frequência e desempatadas pela ordem de aparição — que
    tende a colocar o assunto principal antes.
    """
    from src.infrastructure.search.gdelt import termos_de_busca as termos_gdelt

    return termos_gdelt(texto, maximo=maximo)


class BuscadorGoogleNews:
    """Busca notícias semelhantes no feed RSS de busca do Google Notícias."""

    def __init__(
        self,
        idioma: str = "pt-BR",
        pais: str = "BR",
        timeout: float = TIMEOUT_PADRAO,
        cliente: httpx.Client | None = None,
        marcapasso: Marcapasso | None = None,
        disjuntor: Disjuntor | None = None,
    ):
        self.idioma = idioma
        self.pais = pais
        self.timeout = timeout
        self._cliente = cliente
        # Injetáveis para o teste não esperar o intervalo real nem herdar o estado de
        # falha de outro caso.
        self._marcapasso = marcapasso if marcapasso is not None else _marcapasso
        self._disjuntor = disjuntor if disjuntor is not None else _disjuntor

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        """Top-k notícias relacionadas, da mais à menos relevante.

        Lista vazia só quando o feed respondeu e não havia nada. Indisponibilidade
        levanta :class:`BuscaIndisponivel`, e a N3 traduz isso em sinal indisponível com
        justificativa própria — confundir as duas coisas é o que RN-06 proíbe.
        """
        consulta = termos_de_busca(texto)
        if not consulta:
            return []

        if self._disjuntor.aberto():
            raise BuscaIndisponivel(
                "a busca está fora do ar; parei de tentar por alguns minutos"
            )

        try:
            itens, decorrido = self._consultar(consulta)
        except BuscaIndisponivel:
            self._disjuntor.registrar_falha()
            raise

        self._disjuntor.registrar_sucesso()
        _log.info(
            "Google Notícias: %d itens para %r em %.1fs",
            len(itens),
            consulta,
            decorrido,
        )
        # O feed devolve até 100 itens; a similaridade é derivada da posição, então o
        # corte tem de vir antes dela, ou o segundo resultado já valeria 0,99.
        recortados = itens[: max(1, top_k)]
        return [
            self._converter(item, posicao, len(recortados))
            for posicao, item in enumerate(recortados)
        ]

    def _consultar(self, consulta: str) -> tuple[list[ElementTree.Element], float]:
        parametros = {
            "q": consulta,
            "hl": self.idioma,
            "gl": self.pais,
            "ceid": f"{self.pais}:{self.idioma.split('-')[0]}",
        }
        url = f"{URL_BUSCA}?{urllib.parse.urlencode(parametros)}"

        self._marcapasso.aguardar()
        inicio = time.monotonic()
        try:
            resposta = self._requisitar(url)
        except httpx.TimeoutException as erro:
            raise BuscaIndisponivel(
                f"o Google Notícias não respondeu em {self.timeout:.0f}s"
            ) from erro
        except httpx.HTTPError as erro:
            raise BuscaIndisponivel(f"falha de rede na busca: {erro}") from erro
        decorrido = time.monotonic() - inicio

        if resposta.status_code == 429:
            raise BuscaIndisponivel("limite de uso da busca estourado")
        if resposta.status_code >= 400:
            raise BuscaIndisponivel(
                f"a busca devolveu HTTP {resposta.status_code}"
            )

        try:
            raiz = ElementTree.fromstring(resposta.text)
        except ElementTree.ParseError as erro:
            raise BuscaIndisponivel(f"feed ilegível: {erro}") from erro

        return raiz.findall(".//item"), decorrido

    def _requisitar(self, url: str) -> httpx.Response:
        cabecalhos = {"user-agent": AGENTE}
        if self._cliente is not None:
            return self._cliente.get(url, headers=cabecalhos)
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as cliente:
            return cliente.get(url, headers=cabecalhos)

    @staticmethod
    def _texto(item: ElementTree.Element, etiqueta: str) -> str:
        elemento = item.find(etiqueta)
        return (elemento.text or "").strip() if elemento is not None else ""

    @classmethod
    def _converter(
        cls, item: ElementTree.Element, posicao: int, total: int
    ) -> DocumentoRelacionado:
        """Traduz um item do feed, derivando a similaridade da posição no ranking.

        O feed não expõe score de relevância, então a posição é a única aproximação
        disponível — a mesma escolha, e a mesma limitação, do adaptador do GDELT. O
        primeiro resultado recebe 1,0 e os seguintes decaem linearmente.
        """
        titulo = cls._texto(item, "title")
        fonte_elemento = item.find("source")
        nome_da_fonte = (
            (fonte_elemento.text or "").strip() if fonte_elemento is not None else ""
        )
        url_da_fonte = (
            fonte_elemento.get("url", "") if fonte_elemento is not None else ""
        )

        # O domínio vem do `<source url>`, não do `<link>`, que é redirecionador do
        # Google — ver o cabeçalho do módulo.
        dominio = veiculos.normalizar_dominio(url_da_fonte) or ""

        # O Google repete o nome do veículo no fim do título. Tirar evita que a
        # evidência enviada à N4 termine sempre com " - Folha de S.Paulo".
        if nome_da_fonte and titulo.endswith(f" - {nome_da_fonte}"):
            titulo = titulo[: -len(f" - {nome_da_fonte}")].strip()

        similaridade = 1.0 - (posicao / total) if total > 1 else 1.0
        return DocumentoRelacionado(
            titulo=titulo,
            url=cls._texto(item, "link") or None,
            fonte=dominio or nome_da_fonte,
            similaridade=round(max(0.0, min(1.0, similaridade)), 4),
            # Posição no ranking não é comparação de texto: S-13 não pode usá-la como
            # medida de cópia. Ver ``DocumentoRelacionado.similaridade_textual``.
            similaridade_textual=False,
            fonte_confiavel=veiculos.e_confiavel(url_da_fonte) if url_da_fonte else False,
            data_publicacao=cls._texto(item, "pubDate") or None,
        )
