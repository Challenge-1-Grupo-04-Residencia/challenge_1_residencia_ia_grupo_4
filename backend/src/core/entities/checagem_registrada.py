"""Uma checagem concluída, guardada para o feed e o histórico (RF-42, RF-43).

É um resumo, não a checagem inteira: o feed precisa do bastante para render um cartão
clicável, e guardar o texto completo de toda notícia consultada seria armazenar
conteúdo de terceiros sem necessidade.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from src.core.entities.claim import Dificuldade, DocumentoRelacionado
from src.core.entities.signal import Sinal

#: Quanto do texto original entra no resumo do feed.
TAMANHO_DO_TRECHO = 180


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class ChecagemRegistrada(BaseModel):
    """Resumo publicável de uma checagem já feita."""

    id: str
    #: Começo do texto consultado, o suficiente para reconhecer a notícia no feed.
    trecho: str
    url: str | None = None
    veracidade: float | None
    faixa: str
    #: RN-03: opinião e sátira entram no feed sem porcentagem.
    exibe_porcentagem: bool = True
    confianca: float
    camada_parada: str
    dificuldade: Dificuldade = Dificuldade.MEDIANO
    regra_aplicada: str | None = None
    explicacao: str = ""
    fontes_citadas: list[str] = Field(default_factory=list)
    checada_em: datetime = Field(default_factory=_agora)

    # Guardados para responder a perguntas de acompanhamento (RF-04) sem refazer a
    # checagem: a N3 é a camada mais cara depois da N4, e repetir a busca só para
    # responder "quais fontes você viu?" seria desperdício.
    evidencias: list[str] = Field(default_factory=list)
    sinais: list[Sinal] = Field(default_factory=list)
    #: As publicações encontradas, com título e veículo. Guardadas porque uma URL
    #: sozinha não serve: o buscador devolve link de redirecionador, e uma resposta com
    #: 500 caracteres de `news.google.com/rss/articles/CBMijwJB...` não permite a
    #: ninguém ver quem publicou — o contrário do que RN-05 pede.
    documentos_relacionados: list[DocumentoRelacionado] = Field(default_factory=list)

    @staticmethod
    def resumir(texto: str) -> str:
        """Corta o texto no limite do feed, sem partir palavra no meio."""
        limpo = " ".join(texto.split())
        if len(limpo) <= TAMANHO_DO_TRECHO:
            return limpo
        cortado = limpo[:TAMANHO_DO_TRECHO]
        espaco = cortado.rfind(" ")
        if espaco > TAMANHO_DO_TRECHO // 2:
            cortado = cortado[:espaco]
        return cortado + "…"
