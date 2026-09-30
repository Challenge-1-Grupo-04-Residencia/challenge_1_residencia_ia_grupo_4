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

from src.core.entities.signal import PESO_TOTAL, Dimensao, Sinal


class Faixa(str, Enum):
    """Rótulo mostrado ao usuário. Nunca afirma certeza absoluta (RN-12)."""

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
C_MIN = 0.7

#: Fora deste intervalo o score é decisivo o bastante para encerrar a checagem.
ZONA_DE_DUVIDA = (25.0, 75.0)

#: Abaixo desta confiança o resultado final é Inconclusivo (RN-04).
C_INCONCLUSIVO = 0.5


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


def cobertura(sinais: list[Sinal]) -> float:
    """Fração do peso total do catálogo que foi efetivamente observada (0 a 1)."""
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

    É ``1 - σ`` sobre os scores por dimensão. Com uma só dimensão observada o desvio é
    zero e a concordância vale 1; isso não infla o resultado porque a cobertura, que
    multiplica este fator, permanece baixa.
    """
    por_dimensao = list(score_por_dimensao(sinais).values())
    if len(por_dimensao) < 2:
        return 1.0
    return 1.0 - pstdev(por_dimensao)


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
