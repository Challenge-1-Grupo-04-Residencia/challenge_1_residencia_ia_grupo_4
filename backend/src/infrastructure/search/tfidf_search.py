"""Busca por similaridade sobre um corpus local, com TF-IDF (RF-27).

É a implementação de partida da porta :class:`BuscadorDeNoticias`: roda offline, sem
chave de API e sem custo, sobre os datasets já padronizados do projeto. Serve para
desenvolver e testar a camada N3 enquanto o acesso ao GDELT não está resolvido, e
continua útil depois como índice do histórico de checagens da própria Vera.

TF-IDF casa por **palavra**, não por sentido: duas reportagens sobre o mesmo fato com
vocabulário diferente ficam distantes. Para a similaridade semântica que a US pede em
sua plenitude, a substituição é trocar o vetorizador por embeddings de sentença,
mantendo esta mesma interface.
"""

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.core.entities.claim import DocumentoRelacionado
from src.infrastructure.sources import veiculos

#: Português tem muita palavra funcional curta; sem removê-las o cosseno mede
#: gramática em vez de assunto.
STOPWORDS_PT = [
    "a", "à", "agora", "ao", "aos", "as", "às", "até", "com", "como", "da", "das",
    "de", "dele", "dela", "deles", "delas", "depois", "do", "dos", "e", "é", "ela",
    "elas", "ele", "eles", "em", "entre", "era", "essa", "esse", "esta", "este",
    "eu", "foi", "foram", "há", "isso", "isto", "já", "la", "lhe", "mais", "mas",
    "me", "mesmo", "meu", "muito", "na", "não", "nas", "nem", "no", "nos", "nós",
    "o", "os", "ou", "para", "pela", "pelo", "por", "que", "quem", "se", "sem",
    "ser", "seu", "sua", "são", "só", "também", "te", "tem", "ter", "teu", "um",
    "uma", "você", "vocês",
]


@dataclass
class Documento:
    """Uma notícia do corpus indexado."""

    titulo: str
    texto: str
    url: str | None = None
    fonte: str = ""
    data_publicacao: str | None = None


class BuscadorTfidf:
    """Índice TF-IDF em memória sobre uma lista de documentos.

    O índice é construído uma vez na instanciação. Para um corpus grande, reconstruir a
    cada requisição seria o gargalo da N3 — por isso a instância deve ser reaproveitada
    entre chamadas.
    """

    def __init__(self, documentos: list[Documento], min_similaridade: float = 0.1):
        self.documentos = documentos
        #: Abaixo deste cosseno dois textos só compartilham palavras comuns, e devolvê-los
        #: como "notícia semelhante" produziria corroboração falsa. O valor 0,10 vem da
        #: EDA do grupo em 28/09 (ver o registro de descobertas em docs/investigacao.md):
        #: dá 79,4% de recall com 0,6% de falsos positivos.
        self.min_similaridade = min_similaridade
        self._vetorizador: TfidfVectorizer | None = None
        self._matriz = None
        if documentos:
            self._indexar()

    def _indexar(self) -> None:
        self._vetorizador = TfidfVectorizer(
            stop_words=STOPWORDS_PT,
            # Bigramas capturam nomes compostos ("ministério da saúde"), que são o que
            # mais distingue um fato de outro.
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
        )
        corpus = [f"{d.titulo} {d.texto}" for d in self.documentos]
        self._matriz = self._vetorizador.fit_transform(corpus)

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        """Top-k documentos mais semelhantes, acima do limiar de similaridade."""
        if not self.documentos or self._vetorizador is None or not texto.strip():
            return []

        consulta = self._vetorizador.transform([texto])
        similaridades = cosine_similarity(consulta, self._matriz)[0]

        ordenados = sorted(
            zip(self.documentos, similaridades, strict=True),
            key=lambda par: par[1],
            reverse=True,
        )

        return [
            DocumentoRelacionado(
                titulo=doc.titulo,
                url=doc.url,
                fonte=doc.fonte or (veiculos.normalizar_dominio(doc.url) or ""),
                similaridade=float(sim),
                fonte_confiavel=veiculos.e_confiavel(doc.url or doc.fonte),
                data_publicacao=doc.data_publicacao,
            )
            for doc, sim in ordenados[:top_k]
            if sim >= self.min_similaridade
        ]
