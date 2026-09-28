from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Senhora Vera API",
    description="Motor de Veracidade de Notícias em Múltiplas Camadas",
    version="0.1.0"
)

class ChecagemRequest(BaseModel):
    texto: str
    url: str | None = None

class ChecagemResponse(BaseModel):
    veracidade: float
    confianca: float
    camada_parada: str
    explicacao: str

@app.post("/api/v1/checar", response_model=ChecagemResponse)
async def checar_noticia(request: ChecagemRequest):
    # Aqui vamos instanciar o Orquestrador da pasta src.core.engine
    # e injetar as dependências (modelos da N2, APIs da N1, etc)
    return ChecagemResponse(
        veracidade=50.0,
        confianca=0.0,
        camada_parada="N0",
        explicacao="Endpoint base configurado. Orquestrador em construção."
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "sistema": "Vera API"}
