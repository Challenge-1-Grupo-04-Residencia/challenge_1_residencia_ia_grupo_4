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
import threading
import time

import httpx

from src.core.entities.claim import DocumentoRelacionado
from src.core.ports.news_search import BuscaIndisponivel
from src.infrastructure.search.tfidf_search import STOPWORDS_PT
from src.infrastructure.sources import veiculos

_log = logging.getLogger(__name__)

URL_API = "https://api.gdeltproject.org/api/v2/doc/doc"

_PALAVRA = re.compile(r"\b[\wÀ-ÿ]{4,}\b", re.UNICODE)
_STOPWORDS = frozenset(STOPWORDS_PT)

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


class _Marcapasso:
    """Garante o intervalo mínimo entre chamadas à API, entre threads.

    O endpoint da API roda em *threadpool*, então duas requisições simultâneas chegariam
    aqui ao mesmo tempo e tomariam 429 juntas. O custo é a segunda esperar; a
    alternativa é as duas falharem.
    """

    def __init__(self, intervalo: float):
        self._intervalo = intervalo
        self._trava = threading.Lock()
        self._ultima_chamada = 0.0

    def aguardar(self) -> None:
        with self._trava:
            espera = self._intervalo - (time.monotonic() - self._ultima_chamada)
            if espera > 0:
                time.sleep(espera)
            self._ultima_chamada = time.monotonic()


#: Compartilhado por todas as instâncias: o limite do GDELT é por IP, não por objeto.
_marcapasso = _Marcapasso(INTERVALO_MINIMO_ENTRE_CHAMADAS)


class _Disjuntor:
    """Para de tentar depois de algumas falhas seguidas, e volta a tentar depois.

    Sem isto, com o GDELT fora do ar **toda** checagem paga o timeout inteiro — 25 s de
    espera para chegar à mesma conclusão da checagem anterior. Era o caso na medição:
    o serviço respondia 429 ou estourava o tempo em 100% das consultas, e cada usuário
    esperava por nada.

    Também é questão de boa vizinhança: insistir numa API que acabou de nos pedir para
    desacelerar é o que mantém o 429 vindo.

    Um sucesso fecha o disjuntor. Enquanto ele está aberto a camada recebe
    :class:`BuscaIndisponivel` na hora, e por RN-06 S-11 fica indisponível — o mesmo
    resultado de antes, sem a espera.
    """

    def __init__(self, falhas_para_abrir: int, descanso: float):
        self._falhas_para_abrir = falhas_para_abrir
        self._descanso = descanso
        self._trava = threading.Lock()
        self._falhas = 0
        self._aberto_desde = 0.0

    def aberto(self) -> bool:
        with self._trava:
            if self._falhas < self._falhas_para_abrir:
                return False
            if time.monotonic() - self._aberto_desde >= self._descanso:
                # Passado o descanso, deixa uma tentativa passar para sondar o serviço.
                self._falhas = self._falhas_para_abrir - 1
                return False
            return True

    def registrar_falha(self) -> None:
        with self._trava:
            self._falhas += 1
            if self._falhas == self._falhas_para_abrir:
                self._aberto_desde = time.monotonic()
                _log.warning(
                    "GDELT: %d falhas seguidas, parando de tentar por %.0fs",
                    self._falhas,
                    self._descanso,
                )

    def registrar_sucesso(self) -> None:
        with self._trava:
            self._falhas = 0


_disjuntor = _Disjuntor(FALHAS_PARA_ABRIR, DESCANSO_DO_DISJUNTOR)


class BuscadorGdelt:
    """Busca notícias semelhantes na GDELT Doc 2.0 API."""

    def __init__(
        self,
        idioma: str = "portuguese",
        timeout: float = TIMEOUT_PADRAO,
        cliente: httpx.Client | None = None,
        marcapasso: _Marcapasso | None = None,
        disjuntor: "_Disjuntor | None" = None,
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
            fonte_confiavel=veiculos.e_confiavel(url or artigo.get("domain")),
            data_publicacao=artigo.get("seendate"),
        )
