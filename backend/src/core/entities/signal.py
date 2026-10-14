"""Catálogo de sinais da Vera.

Cada sinal é uma evidência isolada que aponta para veracidade (``s`` perto de 1) ou
falsidade (``s`` perto de 0). O score final é a média ponderada dos sinais
**disponíveis** — um sinal sem dado é excluído do cálculo e nunca vale zero (RN-06).

Os pesos vêm de ``docs/produto/classificacao.md`` e são hipótese de partida: a
calibração com dataset rotulado (RNF-07) deve alterá-los, registrando a mudança no
histórico de calibração daquela página.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Dimensao(str, Enum):
    """As três perguntas que a Vera faz sobre uma notícia."""

    FONTE = "fonte"
    CONTEUDO = "conteudo"
    CORROBORACAO = "corroboracao"


class DefinicaoSinal(BaseModel):
    """Entrada imutável do catálogo: o que o sinal mede e quanto ele pesa."""

    id: str
    nome: str
    peso: float
    dimensao: Dimensao
    camada: str


class Sinal(BaseModel):
    """Um sinal já medido para uma notícia concreta.

    Um sinal tem **três** estados, e não dois. Confundir os dois últimos foi o que
    deixava toda notícia verdadeira em Inconclusivo:

    1. **Medido**, com ``score``. Entra no cálculo de V e conta como cobertura.
    2. **Aferido sem achado** (``score`` nulo, ``aferido`` verdadeiro). O detector
       rodou e não encontrou nada para relatar — texto sem gritaria para S-07, sem
       insulto para S-08. Não entra em V, porque ausência de manipulação não é
       evidência de verdade; mas também **não derruba a cobertura**, porque não houve
       falha de medição: olhamos e não havia o que anotar.
    3. **Não medido** (``score`` nulo, ``aferido`` falso). A camada não rodou, a API não
       respondeu, o texto era curto demais. É lacuna de verdade: sai do cálculo (RN-06)
       e derruba a cobertura, e portanto a confiança.

    Os estados 2 e 3 têm a mesma aparência no JSON — ``score: null`` — e significados
    opostos, do mesmo jeito que "medi e está ruim" e "não consegui medir" são opostos.
    """

    id: str
    nome: str
    peso: float
    dimensao: Dimensao
    camada: str
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    #: A medição foi executada? Ver os três estados no docstring da classe.
    aferido: bool = False
    justificativa: str = ""

    @property
    def disponivel(self) -> bool:
        return self.score is not None

    @property
    def e_lacuna(self) -> bool:
        """Não foi possível medir — o estado que derruba a cobertura."""
        return self.score is None and not self.aferido


# --- Dimensão 0 · Cache · Pontuação máxima imediata --------------------------------
# "Alguém já desmentiu isso? Se sim, a checagem para aqui."

S00 = DefinicaoSinal(
    id="S-00",
    nome="Checagem oficial anterior (Cache)",
    peso=0,
    dimensao=Dimensao.CORROBORACAO,
    camada="N0",
)

# --- Dimensão 1 · Fonte · 35 pontos ------------------------------------------------
# "Quem publicou? Esse veículo teve outras notícias falsas recentemente?"

S00 = DefinicaoSinal(
    id="S-00",
    nome="Checagem em cache",
    peso=0,
    dimensao=Dimensao.FONTE,
    camada="N0",
)
S01 = DefinicaoSinal(
    id="S-01",
    nome="Reputação do veículo na base curada",
    peso=12,
    dimensao=Dimensao.FONTE,
    camada="N1",
)
S02 = DefinicaoSinal(
    id="S-02",
    nome="Histórico recente de fakes do domínio (12 meses)",
    peso=8,
    dimensao=Dimensao.FONTE,
    camada="N1",
)
S03 = DefinicaoSinal(
    id="S-03",
    nome="Idade do domínio",
    peso=6,
    dimensao=Dimensao.FONTE,
    camada="N1",
)
S04 = DefinicaoSinal(
    id="S-04",
    nome="Transparência da página (autor, data, expediente, contato)",
    peso=5,
    dimensao=Dimensao.FONTE,
    camada="N1",
)
S05 = DefinicaoSinal(
    id="S-05",
    nome="Autor identificável",
    peso=4,
    dimensao=Dimensao.FONTE,
    camada="N1",
)

# --- Dimensão 2 · Conteúdo · 25 pontos ---------------------------------------------
# "Como está escrito? O que no texto entrega que algo é falso?"

S06 = DefinicaoSinal(
    id="S-06",
    nome="Classificador estilístico (TF-IDF + SVM/RL)",
    peso=10,
    dimensao=Dimensao.CONTEUDO,
    camada="N2",
)
S07 = DefinicaoSinal(
    id="S-07",
    nome="Sensacionalismo",
    peso=5,
    dimensao=Dimensao.CONTEUDO,
    camada="N2",
)
S08 = DefinicaoSinal(
    id="S-08",
    nome="Intensidade emocional",
    peso=5,
    dimensao=Dimensao.CONTEUDO,
    camada="N2",
)
S09 = DefinicaoSinal(
    id="S-09",
    nome="Cita fontes verificáveis",
    peso=3,
    dimensao=Dimensao.CONTEUDO,
    camada="N2",
)
# Detectores de texto gerado por IA são pouco confiáveis, e texto escrito por IA não é
# falso por definição — por isso S-10 entra como indício fraco.
S10 = DefinicaoSinal(
    id="S-10",
    nome="Probabilidade de texto gerado por IA",
    peso=2,
    dimensao=Dimensao.CONTEUDO,
    camada="N2",
)

# --- Dimensão 3 · Corroboração · 40 pontos -----------------------------------------
# "A mesma notícia está em outros sites? As fontes usadas são corretas? É plágio?"

S11 = DefinicaoSinal(
    id="S-11",
    nome="Veículos confiáveis que publicaram o mesmo fato",
    peso=15,
    dimensao=Dimensao.CORROBORACAO,
    camada="N3",
)
S12 = DefinicaoSinal(
    id="S-12",
    nome="NLI: evidências sustentam ou contradizem as alegações",
    peso=20,
    dimensao=Dimensao.CORROBORACAO,
    camada="N4",
)
S13 = DefinicaoSinal(
    id="S-13",
    nome="Originalidade (é cópia alterada de outra fonte?)",
    peso=5,
    dimensao=Dimensao.CORROBORACAO,
    camada="N3",
)

CATALOGO: dict[str, DefinicaoSinal] = {
    d.id: d
    for d in (S00, S01, S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S12, S13)
}

#: Soma dos pesos de todos os sinais possíveis, inclusive os que nenhuma camada mede
#: ainda. Serve de referência de maturidade do produto, não de base da confiança.
PESO_TOTAL: float = sum(d.peso for d in CATALOGO.values())

#: Camadas que existem no código hoje. N0 (cache) e N1 (fonte) ainda não foram escritas.
CAMADAS_ATIVAS: frozenset[str] = frozenset({"N2", "N3", "N4"})

#: S-10 é ``Won't`` no MoSCoW: detectores de texto por IA são pouco confiáveis e texto
#: escrito por IA não é falso por definição. Nunca será medido, então não pode entrar no
#: denominador da cobertura.
SINAIS_FORA_DE_ESCOPO: frozenset[str] = frozenset({"S-10"})


def mensuravel(definicao: DefinicaoSinal) -> bool:
    """O produto **sabe** medir este sinal hoje?

    Distinção que o cálculo da confiança precisa fazer e que ``PESO_TOTAL`` não faz:
    "não consegui medir nesta notícia" é informação sobre a notícia e deve derrubar a
    confiança; "ninguém implementou esta camada ainda" é informação sobre o nosso
    código e não diz nada sobre a notícia. Punir a segunda travava a confiança em 0,63
    no teto, o que tornava a regra de parada de RN-07 matematicamente inalcançável.
    """
    return (
        definicao.camada in CAMADAS_ATIVAS
        and definicao.id not in SINAIS_FORA_DE_ESCOPO
    )


#: Soma dos pesos dos sinais que alguma camada implementada sabe medir. É o denominador
#: da cobertura, e cresce sozinho conforme N0 e N1 entrarem — sem retocar limiar nenhum.
PESO_MENSURAVEL: float = sum(d.peso for d in CATALOGO.values() if mensuravel(d))


def _montar(
    id_sinal: str, score: float | None, aferido: bool, justificativa: str
) -> Sinal:
    """Monta o sinal a partir da definição de catálogo.

    Usar o catálogo em vez de construir :class:`Sinal` na mão garante que peso,
    dimensão e camada não sejam redigitados em cada camada.
    """
    definicao = CATALOGO[id_sinal]
    return Sinal(
        id=definicao.id,
        nome=definicao.nome,
        peso=definicao.peso,
        dimensao=definicao.dimensao,
        camada=definicao.camada,
        score=score,
        aferido=aferido,
        justificativa=justificativa,
    )


def medir(id_sinal: str, score: float | None, justificativa: str = "") -> Sinal:
    """Sinal medido, com valor.

    Aceita ``score`` nulo por compatibilidade com as camadas que ainda não escolheram
    entre :func:`sem_achado` e :func:`nao_medido`; nesse caso o sinal é tratado como
    lacuna, que é o comportamento conservador.
    """
    return _montar(id_sinal, score, aferido=score is not None,
                   justificativa=justificativa)


def sem_achado(id_sinal: str, justificativa: str = "") -> Sinal:
    """O detector rodou e não encontrou nada para relatar.

    Não entra no cálculo de V e **não** derruba a cobertura. É o caso de S-07 num texto
    sem gritaria, de S-08 num texto sem insulto, e de S-13 com um buscador que devolve
    títulos e não compara textos: em nenhum deles houve falha de medição.
    """
    return _montar(id_sinal, None, aferido=True, justificativa=justificativa)


def nao_medido(id_sinal: str, justificativa: str = "") -> Sinal:
    """Não foi possível medir: camada não rodou, API fora, texto curto demais.

    Sai do cálculo por RN-06 e derruba a cobertura — é a lacuna que deve deixar a Vera
    menos confiante.
    """
    return _montar(id_sinal, None, aferido=False, justificativa=justificativa)
