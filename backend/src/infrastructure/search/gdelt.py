"""Adaptador da GDELT Doc 2.0 API para busca de notícias semelhantes (RF-27).

O GDELT indexa notícias do mundo todo em tempo quase real e não exige chave de API, o
que o torna a fonte de corroboração mais barata disponível para a N3.

A API casa por **palavra-chave**, não por similaridade semântica: este adaptador extrai
os termos mais distintivos do texto e usa a similaridade devolvida pelo ranking do
próprio GDELT como aproximação. Quando o corpus local por embeddings estiver pronto, o
ideal é reordenar estes resultados por similaridade real.
"""

import re

import httpx

from src.core.entities.claim import DocumentoRelacionado
from src.infrastructure.search.tfidf_search import STOPWORDS_PT
from src.infrastructure.sources import veiculos

URL_API = "https://api.gdeltproject.org/api/v2/doc/doc"

_PALAVRA = re.compile(r"\b[\wÀ-ÿ]{4,}\b", re.UNICODE)
_STOPWORDS = frozenset(STOPWORDS_PT)


def termos_de_busca(texto: str, maximo: int = 8) -> str:
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
    for p in palavras:
        frequencia[p] = frequencia.get(p, 0) + 1
    # Desempata pela ordem de aparição, que tende a colocar o assunto principal antes.
    ordem = {p: i for i, p in enumerate(dict.fromkeys(palavras))}
    melhores = sorted(frequencia, key=lambda p: (-frequencia[p], ordem[p]))[:maximo]
    return " ".join(melhores)


class BuscadorGdelt:
    """Busca notícias semelhantes na GDELT Doc 2.0 API."""

    def __init__(
        self,
        idioma: str = "portuguese",
        timeout: float = 8.0,
        cliente: httpx.Client | None = None,
    ):
        self.idioma = idioma
        #: A N3 tem orçamento de 8 s de latência; um timeout maior estouraria a meta.
        self.timeout = timeout
        self._cliente = cliente

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        """Top-k notícias relacionadas. Devolve lista vazia se a busca falhar.

        Indisponibilidade de rede não é evidência de falsidade: a N3 traduz a lista
        vazia em sinal indisponível (RN-06), não em score zero.
        """
        consulta = termos_de_busca(texto)
        if not consulta:
            return []

        parametros = {
            "query": f"{consulta} sourcelang:{self.idioma}",
            "mode": "artlist",
            "format": "json",
            "maxrecords": str(max(1, min(top_k, 50))),
            "sort": "hybridrel",
        }

        try:
            if self._cliente is not None:
                resposta = self._cliente.get(URL_API, params=parametros)
            else:
                with httpx.Client(timeout=self.timeout) as cliente:
                    resposta = cliente.get(URL_API, params=parametros)
            resposta.raise_for_status()
            artigos = resposta.json().get("articles", [])
        except (httpx.HTTPError, ValueError, KeyError):
            return []

        return [self._converter(a, posicao, len(artigos)) for posicao, a in enumerate(artigos)]

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
            titulo=artigo.get("title", "").strip(),
            url=url,
            fonte=artigo.get("domain", "") or (veiculos.normalizar_dominio(url) or ""),
            similaridade=round(max(0.0, min(1.0, similaridade)), 4),
            fonte_confiavel=veiculos.e_confiavel(url or artigo.get("domain")),
            data_publicacao=artigo.get("seendate"),
        )
