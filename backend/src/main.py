"""API HTTP da Senhora Vera.

Expõe o motor de veracidade como serviço. Esta camada não decide nada sobre checagem:
ela monta o pipeline, converte JSON em entidade de domínio e traduz o veredito de volta
para JSON. Toda a regra vive em ``src.core``.
"""

import logging
import uuid
from datetime import datetime
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.core.engine import follow_up, scoring, triagem
from src.core.engine.n2_content import CamadaN2Conteudo
from src.core.engine.n3_corroboration import CamadaN3Corroboracao
from src.core.engine.n4_nli import CamadaN4Inferencia
from src.core.engine.orchestrator import Orquestrador
from src.core.entities.checagem_registrada import ChecagemRegistrada
from src.core.entities.claim import DocumentoRelacionado, NoticiaRequest
from src.infrastructure.storage.historico_memoria import HistoricoEmMemoria

_log = logging.getLogger(__name__)

app = FastAPI(
    title="Senhora Vera API",
    description="Motor de Veracidade de Notícias em Múltiplas Camadas",
    version="0.3.0",
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
    #: ``score`` nulo com ``aferido`` verdadeiro significa "olhei e não havia o que
    #: anotar"; com ``aferido`` falso significa "não consegui medir". Os dois chegam
    #: como ``score: null`` e querem dizer coisas opostas.
    aferido: bool
    justificativa: str


class TriagemRequest(BaseModel):
    """O que o usuário digitou, para a API dizer o que fazer com aquilo."""

    texto: str = Field(min_length=1)
    #: Existe um resultado na tela sobre o qual a pessoa possa estar perguntando?
    tem_checagem_anterior: bool = False


class TriagemResponse(BaseModel):
    """Para onde a mensagem deve ir, decidido no núcleo e não na interface."""

    #: Um valor de :class:`triagem.Natureza`. Só ``alegacao`` vai para ``/checar``, e
    #: só ``acompanhamento`` vai para ``/perguntar``.
    natureza: str
    #: A fala da Vera, já pronta, quando a mensagem é conversa e não checagem.
    resposta: str | None = None


class PerguntaRequest(BaseModel):
    """Pergunta de acompanhamento sobre um resultado já entregue (RF-04)."""

    id_checagem: str = Field(description="ID devolvido pela checagem original")
    pergunta: str = Field(min_length=1)


class FonteCitadaResponse(BaseModel):
    """Publicação citada numa resposta de acompanhamento (RN-05)."""

    titulo: str
    url: str
    veiculo: str
    confiavel: bool


class RespostaResponse(BaseModel):
    texto: str
    assunto: str
    fontes: list[FonteCitadaResponse] = []
    sinais_citados: list[str] = []


class ChecagemDoFeed(BaseModel):
    """Cartão do feed de últimas checagens (RF-43)."""

    id: str
    trecho: str
    url: str | None = None
    veracidade: float | None
    faixa: str
    exibe_porcentagem: bool
    confianca: float
    camada_parada: str
    dificuldade: str
    regra_aplicada: str | None = None
    checada_em: datetime


class ChecagemResponse(BaseModel):
    """Resultado publicável. Sempre traz os campos de RN-05."""

    #: Identificador desta checagem, usado nas perguntas de acompanhamento (RF-04).
    id: str
    veracidade: float | None
    confianca: float
    faixa: str
    camada_parada: str
    dificuldade: str
    explicacao: str
    exibe_porcentagem: bool
    regra_aplicada: str | None = None
    cobertura: float
    #: Fração dos 100 pontos do catálogo completo que foi observada. Menor que
    #: ``cobertura`` enquanto houver camada não implementada, e serve para a Vera poder
    #: dizer quanto do que ela gostaria de olhar ainda não existe (RF-33).
    cobertura_do_catalogo: float
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
    from src.infrastructure.search.google_news import BuscadorGoogleNews

    n2 = CamadaN2Conteudo()
    # Google Notícias e não GDELT: medidos lado a lado em 05/10, o GDELT respondia em
    # 15 a 23 s, aceitava uma consulta a cada 5 s e devolvia zero resultados em
    # português, o que deixava a dimensão Corroboração — 40 dos 100 pontos — sem
    # medição nenhuma em produção. O feed do Google responde em ~1 s. O adaptador do
    # GDELT segue no repositório atrás da mesma porta, para quem quiser comparar.
    n3 = CamadaN3Corroboracao(BuscadorGoogleNews())
    n4 = CamadaN4Inferencia()
    # N0 e N1 ainda não existem, então a corrente começa na N2. Por RN-07 a N4 só roda
    # se as anteriores não atingirem a regra de parada — o encadeamento já garante isso.
    n2.set_proxima(n3).set_proxima(n4)
    return Orquestrador(n2)


@lru_cache(maxsize=1)
def obter_historico() -> HistoricoEmMemoria:
    """Histórico de checagens, compartilhado entre requisições.

    Hoje é em memória e se perde ao reiniciar o servidor. A porta
    ``HistoricoDeChecagens`` existe para que a troca por persistência real não toque
    no núcleo nem nesta camada.
    """
    return HistoricoEmMemoria()


def _para_response(sinal) -> SinalResponse:
    return SinalResponse(
        id=sinal.id,
        nome=sinal.nome,
        peso=sinal.peso,
        dimensao=sinal.dimensao.value,
        camada=sinal.camada,
        score=sinal.score,
        aferido=sinal.aferido,
        justificativa=sinal.justificativa,
    )


@app.post("/api/v1/checar", response_model=ChecagemResponse)
def checar_noticia(request: ChecagemRequest) -> ChecagemResponse:
    """Roda o pipeline de camadas e devolve o veredito com o detalhamento dos sinais.

    É ``def`` e não ``async def`` de propósito. O pipeline faz I/O **bloqueante** — a
    busca da N3 por ``httpx.Client`` e a chamada da N4 por ``urllib`` —, e numa corrotina
    isso trava o *event loop*: duas requisições simultâneas foram medidas serializando
    perfeitamente (8,3 s e 16,5 s, total 16,5 s), e uma resposta já pronta ficava retida
    até a outra liberar o laço. Com o endpoint síncrono o FastAPI executa em
    *threadpool*, e as requisições deixam de esperar umas pelas outras.
    """
    noticia = NoticiaRequest(texto=request.texto, url=request.url)
    orquestrador = obter_orquestrador()

    try:
        veredito = orquestrador.veredito(noticia)
    except Exception:  # noqa: BLE001 - nenhuma falha interna sai como traceback
        _log.exception("pipeline falhou para texto de %d caracteres", len(request.texto))
        raise HTTPException(
            status_code=503,
            detail=(
                "Me deu um branco aqui, meu bem. Tenta de novo daqui a pouquinho, "
                "visse?"
            ),
        ) from None
    resultado = noticia.resultado
    explicacao = (veredito.motivo_regra + " " + resultado.explicacao).strip()
    id_checagem = uuid.uuid4().hex

    _registrar_no_historico(id_checagem, request, veredito, resultado, explicacao)

    return ChecagemResponse(
        id=id_checagem,
        veracidade=veredito.veracidade,
        confianca=round(veredito.confianca, 4),
        faixa=veredito.faixa.value,
        camada_parada=resultado.camada_atual,
        dificuldade=resultado.dificuldade.value,
        explicacao=explicacao,
        exibe_porcentagem=veredito.exibe_porcentagem,
        regra_aplicada=veredito.regra_aplicada,
        cobertura=round(resultado.cobertura, 4),
        cobertura_do_catalogo=round(resultado.cobertura_do_catalogo, 4),
        principais_sinais=[
            _para_response(s) for s in scoring.principais_sinais(resultado.sinais)
        ],
        sinais=[_para_response(s) for s in resultado.sinais],
        documentos_relacionados=resultado.documentos_relacionados,
        fontes_citadas=resultado.fontes_citadas,
    )


def _registrar_no_historico(
    id_checagem: str, request: ChecagemRequest, veredito, resultado, explicacao: str
) -> None:
    """Guarda a checagem para o feed e para as perguntas de acompanhamento.

    Falha aqui não pode derrubar a resposta: perder uma entrada do feed é muito menos
    grave do que negar ao usuário o resultado que ele pediu.
    """
    try:
        obter_historico().registrar(
            ChecagemRegistrada(
                id=id_checagem,
                trecho=ChecagemRegistrada.resumir(request.texto),
                url=request.url,
                veracidade=veredito.veracidade,
                faixa=veredito.faixa.value,
                exibe_porcentagem=veredito.exibe_porcentagem,
                confianca=round(veredito.confianca, 4),
                camada_parada=resultado.camada_atual,
                dificuldade=resultado.dificuldade,
                regra_aplicada=veredito.regra_aplicada,
                explicacao=explicacao,
                fontes_citadas=list(resultado.fontes_citadas),
                evidencias=list(resultado.evidencias),
                sinais=list(resultado.sinais),
                documentos_relacionados=list(resultado.documentos_relacionados),
            )
        )
    except Exception:  # noqa: BLE001 - o feed nunca derruba a checagem
        pass


@app.post("/api/v1/triagem", response_model=TriagemResponse)
def triar(request: TriagemRequest) -> TriagemResponse:
    """Diz se a mensagem é conversa, pergunta de acompanhamento ou alegação a checar.

    Existe para a interface não precisar adivinhar. Ela adivinhava pelo número de
    palavras — mandava ao acompanhamento tudo com menos de 25 — e o efeito era que,
    depois da primeira checagem, **toda notícia curta** recebia "essa sua pergunta eu
    ainda não sei responder direito" em vez de ser checada.

    É barato: só regra de negócio, sem rede e sem modelo.
    """
    natureza = triagem.classificar(request.texto, request.tem_checagem_anterior)
    conversa = natureza in (
        triagem.Natureza.SAUDACAO,
        triagem.Natureza.CONVERSA,
        triagem.Natureza.AGRADECIMENTO,
    )
    return TriagemResponse(
        natureza=natureza.value,
        resposta=triagem.resposta_para(natureza) if conversa else None,
    )


@app.post("/api/v1/perguntar", response_model=RespostaResponse)
def perguntar(request: PerguntaRequest) -> RespostaResponse:
    """Responde uma pergunta sobre um resultado já entregue (RF-04).

    Usa os sinais e as evidências que a N3 já recuperou, sem refazer a checagem: a
    busca é cara e repeti-la para responder "quais fontes você viu?" seria desperdício.
    """
    checagem = obter_historico().buscar(request.id_checagem)
    if checagem is None:
        raise HTTPException(
            status_code=404,
            detail="Não encontrei essa checagem. Ela pode ter expirado do histórico.",
        )

    resposta = follow_up.responder(request.pergunta, checagem)
    return RespostaResponse(
        texto=resposta.texto,
        assunto=resposta.assunto.value,
        fontes=[
            FonteCitadaResponse(
                titulo=f.titulo, url=f.url, veiculo=f.veiculo, confiavel=f.confiavel
            )
            for f in resposta.fontes
        ],
        sinais_citados=resposta.sinais_citados,
    )


@app.get("/api/v1/checagens/recentes", response_model=list[ChecagemDoFeed])
def checagens_recentes(limite: int = 10) -> list[ChecagemDoFeed]:
    """Últimas checagens, para o feed da página inicial (RF-43)."""
    return [
        ChecagemDoFeed(
            id=c.id,
            trecho=c.trecho,
            url=c.url,
            veracidade=c.veracidade,
            faixa=c.faixa,
            exibe_porcentagem=c.exibe_porcentagem,
            confianca=c.confianca,
            camada_parada=c.camada_parada,
            dificuldade=c.dificuldade.value,
            regra_aplicada=c.regra_aplicada,
            checada_em=c.checada_em,
        )
        for c in obter_historico().recentes(max(1, min(limite, 50)))
    ]


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "sistema": "Vera API"}
