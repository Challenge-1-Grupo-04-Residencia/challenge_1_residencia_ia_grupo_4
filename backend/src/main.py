"""API HTTP da Senhora Vera.

Expõe o motor de veracidade como serviço. Esta camada não decide nada sobre checagem:
ela monta o pipeline, converte JSON em entidade de domínio e traduz o veredito de volta
para JSON. Toda a regra vive em ``src.core``.
"""

from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.core.engine import scoring
from src.core.engine.n2_content import CamadaN2Conteudo
from src.core.engine.n3_corroboration import CamadaN3Corroboracao
from src.core.engine.n4_nli import CamadaN4Inferencia
from src.core.engine.orchestrator import Orquestrador
from src.core.entities.claim import DocumentoRelacionado, NoticiaRequest
from src.core.engine.n0_cache import CamadaN0Cache
from src.core.engine.n1_fonte import CamadaN1Fonte
from src.core.engine.leitor_link import CamadaLeitorLink

app = FastAPI(
    title="Senhora Vera API",
    description="Motor de Veracidade de Notícias em Múltiplas Camadas",
    version="0.2.0",
)

# O frontend roda em outra porta em desenvolvimento, então precisa de CORS. Em produção
# esta lista deve ser restringida ao domínio real da Vera.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChecagemRequest(BaseModel):
    texto: str = Field(min_length=1, description="Texto, afirmação ou link a checar")
    url: str | None = None


class SinalResponse(BaseModel):
    """Um sinal no detalhamento exigido por RF-33."""

    id: str
    nome: str
    peso: float
    dimensao: str
    camada: str
    score: float | None
    justificativa: str


class ChecagemResponse(BaseModel):
    """Resultado publicável. Sempre traz os campos de RN-05."""

    veracidade: float | None
    confianca: float
    faixa: str
    camada_parada: str
    dificuldade: str
    explicacao: str
    exibe_porcentagem: bool
    regra_aplicada: str | None = None
    cobertura: float
    principais_sinais: list[SinalResponse] = []
    sinais: list[SinalResponse] = []
    documentos_relacionados: list[DocumentoRelacionado] = []
    fontes_citadas: list[str] = []


@lru_cache(maxsize=1)
def obter_orquestrador() -> Orquestrador:
    """Monta a corrente de camadas uma única vez.

    O classificador da N2 e o índice de busca são caros de carregar; reconstruí-los a
    cada requisição estouraria as metas de latência das camadas.
    """
    from src.infrastructure.search.gdelt import BuscadorGdelt
    from src.infrastructure.search.pgvector_search import BuscadorVetorial
    from src.infrastructure.search.hibrido_search import BuscadorHibrido

    n0 = CamadaN0Cache()
    n1 = CamadaN1Fonte()
    leitor = CamadaLeitorLink()
    n2 = CamadaN2Conteudo()
    
    buscador_combinado = BuscadorHibrido([BuscadorGdelt(), BuscadorVetorial()])
    n3 = CamadaN3Corroboracao(buscador_combinado)
    
    n4 = CamadaN4Inferencia()

    # O encadeamento garante a sequência correta da arquitetura
    n0.set_proxima(n1).set_proxima(leitor).set_proxima(n2).set_proxima(n3).set_proxima(n4)
    return Orquestrador(n0)


def _para_response(sinal) -> SinalResponse:
    return SinalResponse(
        id=sinal.id,
        nome=sinal.nome,
        peso=sinal.peso,
        dimensao=sinal.dimensao.value,
        camada=sinal.camada,
        score=sinal.score,
        justificativa=sinal.justificativa,
    )


@app.post("/api/v1/checar", response_model=ChecagemResponse)
async def checar_noticia(request: ChecagemRequest) -> ChecagemResponse:
    """Roda o pipeline de camadas e devolve o veredito com o detalhamento dos sinais."""
    noticia = NoticiaRequest(texto=request.texto, url=request.url)
    orquestrador = obter_orquestrador()

    veredito = orquestrador.veredito(noticia)
    resultado = noticia.resultado

    return ChecagemResponse(
        veracidade=veredito.veracidade,
        confianca=round(veredito.confianca, 4),
        faixa=veredito.faixa.value,
        camada_parada=resultado.camada_atual,
        dificuldade=resultado.dificuldade.value,
        explicacao=(veredito.motivo_regra + " " + resultado.explicacao).strip(),
        exibe_porcentagem=veredito.exibe_porcentagem,
        regra_aplicada=veredito.regra_aplicada,
        cobertura=round(resultado.cobertura, 4),
        principais_sinais=[
            _para_response(s) for s in scoring.principais_sinais(resultado.sinais)
        ],
        sinais=[_para_response(s) for s in resultado.sinais],
        documentos_relacionados=resultado.documentos_relacionados,
        fontes_citadas=resultado.fontes_citadas,
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "sistema": "Vera API"}
