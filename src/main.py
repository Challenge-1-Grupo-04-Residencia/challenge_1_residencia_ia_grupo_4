from fastapi import FastAPI
from pydantic import BaseModel
from src.core.entities.claim import NoticiaRequest
from src.core.engine.orchestrator import Orquestrador
from src.core.engine.n2_content import CamadaN2Conteudo

app = FastAPI(
    title="Senhora Vera API",
    description="Motor de Veracidade de Notícias em Múltiplas Camadas",
    version="0.1.0"
)

# Modelo simplificado de resposta para a nossa interface/frontend
class ChecagemResponse(BaseModel):
    veracidade: float
    confianca: float
    camada_parada: str
    explicacao: str

# === MOCKS TEMPORÁRIOS ===
# Criamos essas camadas falsas para podermos ver a "esteira" do Orquestrador 
# funcionando por completo até que seus colegas entreguem o código real delas.
from src.core.engine.orchestrator import CamadaVerificacao

class MockCamadaN1(CamadaVerificacao):
    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        noticia.resultado.camada_atual = "N1"
        noticia.resultado.explicacao += "[N1 FactCheck pulou] "
        return self.repassar(noticia)

class MockCamadaN3(CamadaVerificacao):
    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        noticia.resultado.camada_atual = "N3"
        noticia.resultado.explicacao += " [N3 rodou: Notícia suspeita, mas N3 adicionou pouca confiança]."
        noticia.resultado.confianca += 0.1
        return self.repassar(noticia)
# =========================

@app.post("/api/v1/checar", response_model=ChecagemResponse)
async def checar_noticia(request: NoticiaRequest):
    """
    Endpoint principal que recebe a notícia e repassa para o Orquestrador.
    """
    # 1. Instanciamos a nossa esteira com Mocks + a nossa N2 real
    camada_n1_mock = MockCamadaN1()
    camada_n2_real = CamadaN2Conteudo()
    camada_n3_mock = MockCamadaN3()
    
    # 2. Conectamos os robôs da esteira: N1 -> N2 -> N3
    camada_n1_mock.set_proxima(camada_n2_real).set_proxima(camada_n3_mock)
    
    # 3. Inicializamos o Orquestrador entregando a ponta da esteira (N1)
    orquestrador = Orquestrador(camada_inicial=camada_n1_mock)
    
    # 3. Disparamos a checagem com o texto vindo da internet
    resultado_final = orquestrador.checar(request)
    
    # 4. Retornamos o resultado final limpo para o usuário
    return ChecagemResponse(
        veracidade=resultado_final.resultado.veracidade,
        confianca=resultado_final.resultado.confianca,
        camada_parada=resultado_final.resultado.camada_atual,
        explicacao=resultado_final.resultado.explicacao
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "sistema": "Vera API"}
