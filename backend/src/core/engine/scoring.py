"""Cálculo do score de veracidade e da confiança (RF-09).

Implementa as fórmulas de ``docs/produto/classificacao.md``:

.. math::

    V = 100 \\times \\frac{\\sum_{i \\in D} w_i s_i}{\\sum_{i \\in D} w_i}

    C = \\underbrace{\\frac{\\sum_{i \\in D} w_i}{100}}_{cobertura}
        \\times \\underbrace{(1 - \\sigma_{dimensões})}_{concordância}

Onde ``D`` é o conjunto de sinais **disponíveis**. Um sinal sem dado é excluído do
cálculo e não conta como zero (RN-06) — isso é o que separa "não sabemos" de
"sabemos que é ruim".
"""

from enum import Enum
from statistics import pstdev

from src.core.entities.signal import (
    CATALOGO,
    PESO_TOTAL,
    Dimensao,
    Sinal,
    mensuravel,
)


class Faixa(str, Enum):
    """Rótulo mostrado ao usuário. Nunca afirma certeza absoluta (RN-12)."""

    #: Não houve checagem: a entrada era conversa, não alegação de fato. Não é o mesmo
    #: que ``INCONCLUSIVA``, que é um resultado de checagem — aqui não houve checagem.
    CONVERSA = "Conversa"
    FALSA = "Provavelmente falsa"
    DUVIDOSA = "Duvidosa"
    INCONCLUSIVA = "Inconclusiva"
    VERDADEIRA = "Provavelmente verdadeira"
    CONFIRMADA = "Confirmada por fontes"


#: Limite superior de cada faixa, em ordem crescente. Ver a tabela de faixas em
#: ``docs/produto/classificacao.md``.
_FAIXAS: tuple[tuple[float, Faixa], ...] = (
    (20, Faixa.FALSA),
    (40, Faixa.DUVIDOSA),
    (60, Faixa.INCONCLUSIVA),
    (80, Faixa.VERDADEIRA),
    (100, Faixa.CONFIRMADA),
)

#: Confiança mínima para a Vera parar de subir camadas.
#:
#: O valor é 0,60 e não 0,70 por aritmética, não por gosto: ao fim da N3 a cobertura
#: máxima possível é 43/63 = 0,683, porque S-12 sozinho vale 20 dos 63 pontos
#: mensuráveis. Com o limiar em 0,70 a regra de parada nunca podia ser satisfeita antes
#: da N4, e RN-07 — a razão econômica do produto — era código morto: a LLM rodava em
#: 100% das checagens. Em 0,60 uma notícia de estilo claramente falso e sem nenhuma
#: corroboração encerra na N3, e a N4 fica para os casos em que as camadas baratas
#: discordam entre si.
C_MIN = 0.6

#: Fora deste intervalo o score é decisivo o bastante para encerrar a checagem.
ZONA_DE_DUVIDA = (25.0, 75.0)

#: Abaixo desta confiança o resultado final é Inconclusivo (RN-04).
C_INCONCLUSIVO = 0.5

#: Fator aplicado à concordância quando só **uma** das três dimensões foi observada.
#:
#: Uma dimensão sozinha não concorda com nada: o desvio padrão de um valor é zero, então
#: a concordância daria 1,0 — a nota máxima, por não haver com o que discordar. Isso se
#: sustentava enquanto a cobertura segurava o resultado, mas deixou de segurar quando o
#: denominador passou a ignorar os sinais aferidos sem achado.
#:
#: O estrago medido: "o ministro pediu demissao hoje", cinco palavras sem sujeito
#: definido, saía com **V = 100 e "Confirmada por fontes"**. O texto era curto demais
#: para S-06 e S-09, e a busca por "ministro demissão" acha notícia real sobre algum
#: ministro — então S-11 sozinho, com 15 pontos e nenhuma outra dimensão para
#: contradizê-lo, cravava o veredito.
PENALIDADE_DE_DIMENSAO_UNICA = 0.55


def disponiveis(sinais: list[Sinal]) -> list[Sinal]:
    """Filtra os sinais que têm dado, aplicando RN-06."""
    return [s for s in sinais if s.disponivel]


def calcular_veracidade(sinais: list[Sinal]) -> float | None:
    """Média ponderada dos sinais disponíveis, reescalada para 0–100.

    Devolve ``None`` quando nenhum sinal foi observado: sem evidência não existe score,
    e devolver 50 aqui faria "não sei" parecer "está na dúvida".
    """
    observados = disponiveis(sinais)
    peso_observado = sum(s.peso for s in observados)
    if peso_observado == 0:
        return None
    return 100.0 * sum(s.peso * s.score for s in observados) / peso_observado


def peso_de_referencia(sinais: list[Sinal]) -> float:
    """Denominador da cobertura: o peso que esta checagem **podia** ter observado.

    É o peso dos sinais que alguma camada implementada sabe medir, mais o de qualquer
    sinal que tenha sido efetivamente registrado — este segundo termo mantém a conta
    correta quando uma camada nova começa a emitir sinal antes de entrar em
    ``CAMADAS_ATIVAS``, e impede que a cobertura passe de 1.
    """
    registrados = {s.id for s in sinais}
    # Sinal aferido sem achado sai do denominador: o detector rodou, não havia o que
    # anotar, e isso não é lacuna desta notícia. Mantê-lo aqui travava a cobertura de
    # qualquer notícia escrita em tom sóbrio — que são justamente as verdadeiras — e
    # jogava todas em Inconclusivo por RN-04.
    sem_achado = {s.id for s in sinais if s.score is None and s.aferido}
    return sum(
        d.peso
        for d in CATALOGO.values()
        if (mensuravel(d) or d.id in registrados) and d.id not in sem_achado
    )


def cobertura(sinais: list[Sinal]) -> float:
    """Fração do que a Vera **sabe medir** que foi efetivamente observada (0 a 1).

    O denominador é o peso mensurável, não os 100 pontos do catálogo: sinal de camada
    que ainda não foi escrita não é lacuna desta notícia, é lacuna do nosso código, e
    descontá-lo aqui misturava as duas coisas — travava a confiança em 0,63 no teto e
    com isso tornava a regra de parada de RN-07 inalcançável. Sinal que a camada tentou
    medir e não conseguiu continua derrubando a cobertura, que é o que RN-06 pede.
    """
    referencia = peso_de_referencia(sinais)
    if referencia == 0:
        return 0.0
    return sum(s.peso for s in disponiveis(sinais)) / referencia


def cobertura_do_catalogo(sinais: list[Sinal]) -> float:
    """Fração dos 100 pontos do catálogo completo que foi observada (0 a 1).

    Não entra na confiança: serve à transparência de RF-33, para a Vera poder dizer
    quanto do que ela *gostaria* de olhar ainda não existe.
    """
    return sum(s.peso for s in disponiveis(sinais)) / PESO_TOTAL


def score_por_dimensao(sinais: list[Sinal]) -> dict[Dimensao, float]:
    """Score 0–1 de cada dimensão que tem ao menos um sinal disponível.

    Dimensões sem dado ficam de fora do dicionário, e portanto não entram no cálculo
    de concordância — duas dimensões silenciosas não são duas dimensões que concordam.
    """
    resultado: dict[Dimensao, float] = {}
    for dimensao in Dimensao:
        da_dimensao = [s for s in disponiveis(sinais) if s.dimensao is dimensao]
        peso = sum(s.peso for s in da_dimensao)
        if peso > 0:
            resultado[dimensao] = sum(s.peso * s.score for s in da_dimensao) / peso
    return resultado


def concordancia(sinais: list[Sinal]) -> float:
    """Quanto as dimensões observadas apontam para o mesmo lado (0 a 1).

    É ``1 - σ`` sobre os scores por dimensão, como em
    ``docs/produto/classificacao.md``.

    Amplificar esse desvio foi tentado e desfeito: com a dimensão Conteúdo passando a
    ficar perto de 0,5 — porque S-07 e S-08 viraram detectores silenciosos e S-09
    raramente passa de 0,33 —, qualquer notícia verdadeira bem corroborada apresentava
    uma diferença grande e *estrutural* entre Conteúdo e Corroboração. Punir isso
    jogava toda notícia verdadeira em Inconclusivo por RN-04, medindo uma propriedade
    do nosso catálogo e não uma contradição nas evidências.

    Com uma só dimensão observada não há com o que concordar, e o fator vale
    :data:`PENALIDADE_DE_DIMENSAO_UNICA` em vez de 1,0 — ver a nota lá sobre o veredito
    de 100% que um texto de cinco palavras conseguia arrancar.
    """
    por_dimensao = list(score_por_dimensao(sinais).values())
    if not por_dimensao:
        return 1.0
    if len(por_dimensao) == 1:
        return PENALIDADE_DE_DIMENSAO_UNICA
    return max(0.0, 1.0 - pstdev(por_dimensao))


def calcular_confianca(sinais: list[Sinal]) -> float:
    """Confiança no score: cobertura × concordância, limitada a [0, 1]."""
    c = cobertura(sinais) * concordancia(sinais)
    return max(0.0, min(1.0, c))


def classificar(veracidade: float) -> Faixa:
    """Converte o score 0–100 no rótulo da faixa."""
    for limite, faixa in _FAIXAS:
        if veracidade <= limite:
            return faixa
    return Faixa.CONFIRMADA


def deve_parar(veracidade: float | None, confianca: float) -> bool:
    """Regra de parada (RF-08): confiança suficiente **e** score fora da zona de dúvida.

    Enquanto o score estiver entre 26 e 74 a Vera continua subindo de camada mesmo com
    confiança alta, porque um resultado ambíguo com confiança alta ainda não responde
    a pergunta do usuário.
    """
    if veracidade is None:
        return False
    minimo, maximo = ZONA_DE_DUVIDA
    return confianca >= C_MIN and (veracidade <= minimo or veracidade >= maximo)


def principais_sinais(sinais: list[Sinal], limite: int = 3) -> list[Sinal]:
    """Os sinais que mais empurraram o resultado, para a explicação exigida por RN-05.

    Ordena pela contribuição em pontos absolutos do valor neutro (0,5): um sinal de
    peso alto com score extremo explica mais do que um sinal de peso alto e score
    morno.
    """
    return sorted(
        disponiveis(sinais),
        key=lambda s: s.peso * abs(s.score - 0.5),
        reverse=True,
    )[:limite]
