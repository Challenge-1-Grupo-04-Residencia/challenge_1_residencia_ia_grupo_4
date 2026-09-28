from pydantic import BaseModel, Field

class AnaliseResultado(BaseModel):
    veracidade: float = Field(default=50.0, description="Score de veracidade de 0 a 100")
    confianca: float = Field(default=0.0, description="Confiança na decisão de 0 a 1")
    camada_atual: str = Field(default="N0", description="A última camada executada")
    explicacao: str = Field(default="", description="Motivos da classificação")
    fontes_citadas: list[str] = Field(default_factory=list, description="Lista de URLs de corroboração")

class NoticiaRequest(BaseModel):
    texto: str
    url: str | None = None
    
    # Podemos ir adicionando metadados ao longo do chain
    resultado: AnaliseResultado = Field(default_factory=AnaliseResultado)
