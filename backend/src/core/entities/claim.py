"""Entidades que atravessam o pipeline de checagem.

``NoticiaRequest`` é o objeto que passa de camada em camada. Cada camada acrescenta
sinais ao resultado e chama :meth:`AnaliseResultado.recalcular`, que reaplica as
fórmulas de veracidade e confiança sobre tudo o que já foi medido.

``veracidade`` e ``confianca`` permanecem campos graváveis, e não propriedades
derivadas, para que camadas ainda não migradas para o modelo de sinais continuem
funcionando. O caminho correto, porém, é emitir sinais: o valor gravado direto não
entra na explicação nem na cobertura, então some do detalhamento exigido por RF-33.
"""

from enum import Enum

from pydantic import BaseModel, Field

from src.core.engine import scoring
from src.core.entities.signal import Sinal


class Dificuldade(str, Enum):
    """Quão difícil foi checar, medido pela camada em que a Vera parou (RF-13)."""

    FACIL = "facil"
    MEDIANO = "mediano"
    DIFICIL = "dificil"


#: Camada de parada → dificuldade da checagem.
DIFICULDADE_POR_CAMADA: dict[str, Dificuldade] = {
    # Entrada que a triagem barrou antes do pipeline: não houve checagem para medir.
    "TRIAGEM": Dificuldade.FACIL,
    "N0": Dificuldade.FACIL,
    "N1": Dificuldade.FACIL,
    "N2": Dificuldade.MEDIANO,
    "N3": Dificuldade.MEDIANO,
    "N4": Dificuldade.DIFICIL,
}


class DocumentoRelacionado(BaseModel):
    """Notícia semelhante encontrada na corroboração (N3, RF-27)."""

    titulo: str
    url: str | None = None
    fonte: str = ""
    #: Similaridade semântica com o texto consultado, de 0 a 1.
    similaridade: float = Field(ge=0.0, le=1.0)
    #: O veículo está na base curada como confiável? Alimenta S-11 (RF-28).
    fonte_confiavel: bool = False
    data_publicacao: str | None = None


class AnaliseResultado(BaseModel):
    """Estado acumulado da checagem, do início ao veredito."""

    veracidade: float = Field(default=50.0, description="Score de veracidade de 0 a 100")
    confianca: float = Field(default=0.0, description="Confiança na decisão de 0 a 1")
    camada_atual: str = Field(default="N0", description="A última camada executada")
    explicacao: str = Field(default="", description="Motivos da classificação")
    fontes_citadas: list[str] = Field(
        default_factory=list, description="Lista de URLs de corroboração"
    )
    evidencias: list[str] = Field(
        default_factory=list,
        description="Trechos de texto encontrados pela N3 para a inferência da N4",
    )

    sinais: list[Sinal] = Field(
        default_factory=list, description="Sinais medidos até aqui (S-01 a S-13)"
    )
    documentos_relacionados: list[DocumentoRelacionado] = Field(
        default_factory=list, description="Notícias semelhantes encontradas na N3"
    )

    # Fatos que ativam as regras de negócio, preenchidos pelas camadas.
    veredito_agencia: str | None = None
    agencia: str | None = None
    dominio_impostor: bool = False
    veiculo_imitado: str | None = None
    natureza: str | None = None

    def registrar(self, sinal: Sinal) -> None:
        """Acrescenta um sinal e reaplica as fórmulas.

        Se o mesmo sinal já tiver sido medido, a medição nova substitui a antiga — uma
        camada mais cara pode refinar o que uma camada barata estimou.
        """
        self.sinais = [s for s in self.sinais if s.id != sinal.id] + [sinal]
        self.recalcular()

    def recalcular(self) -> None:
        """Recalcula veracidade e confiança a partir dos sinais registrados."""
        v = scoring.calcular_veracidade(self.sinais)
        if v is not None:
            self.veracidade = v
        self.confianca = scoring.calcular_confianca(self.sinais)

    @property
    def dificuldade(self) -> Dificuldade:
        return DIFICULDADE_POR_CAMADA.get(self.camada_atual, Dificuldade.MEDIANO)

    @property
    def cobertura(self) -> float:
        """Fração do que as camadas existentes sabem medir que foi observada."""
        return scoring.cobertura(self.sinais)

    @property
    def cobertura_do_catalogo(self) -> float:
        """Fração dos 100 pontos do catálogo completo que foi observada."""
        return scoring.cobertura_do_catalogo(self.sinais)


class NoticiaRequest(BaseModel):
    """A notícia em checagem, com o resultado acumulado até a camada atual."""

    texto: str
    url: str | None = None

    resultado: AnaliseResultado = Field(default_factory=AnaliseResultado)
