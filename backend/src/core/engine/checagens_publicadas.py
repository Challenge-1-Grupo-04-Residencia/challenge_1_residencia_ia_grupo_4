"""Lê o veredito de uma checagem já publicada por agência (RF-17, RN-01).

As agências signatárias da IFCN põem o veredito **no título** da checagem, num punhado
de fórmulas fixas:

    É #FAKE que Lula jogou a bandeira do Brasil no chão após votar   (G1 Fato ou Fake)
    É falso que Gilmar Mendes entrou na cabine de votação com celular  (Aos Fatos)
    É #FATO: problema na rede elétrica atrasou funcionamento de urna   (G1 Fato ou Fake)

Isso é verificação humana publicada, e por RN-01 ela **prevalece sobre o score
calculado**: nenhuma combinação de sinais estilísticos vale o que vale uma redação de
checagem tendo ido conferir a alegação concreta.

## Por que isto importa tanto

Sem este módulo, a camada N3 caía numa armadilha que a busca por palavra-chave não
resolve: perguntada sobre "Lula jogou a bandeira no chão", ela encontrava a checagem do
G1, do Aos Fatos e do Boatos, contava **três veículos confiáveis publicando sobre o
assunto** e empurrava S-11 para o máximo — ou seja, a notícia falsa era *corroborada*
pelo próprio desmentido dela. Medido na bateria de exemplos reais.

A outra saída é a N4 ler os títulos e devolver ``CONTRADICTION``, e ela continua sendo
a resposta geral. Mas depender só dela deixa o produto sem defesa quando o provedor de
LLM não está de pé, e gasta a camada mais cara no caso em que a resposta está escrita
com todas as letras no título do resultado.

## A trava contra aplicar o veredito à alegação errada

Uma checagem sobre "bandeira no chão" não pode decidir uma pergunta sobre "resultado da
eleição" só porque as duas mencionam o mesmo político. Por isso o veredito só é adotado
quando a alegação desmentida e o texto do usuário compartilham
:data:`SOBREPOSICAO_MINIMA` do vocabulário de conteúdo da alegação — e exige-se um
mínimo absoluto de palavras em comum, porque fração alta sobre duas palavras não
significa nada.
"""

import re
import unicodedata
from dataclasses import dataclass

#: Fórmulas que abrem uma checagem com veredito **falso**. A ordem não importa; o que
#: importa é que todas sejam de alta precisão: um falso positivo aqui aplica RN-01
#: indevidamente e o score vai a 10 sem apelação.
PADROES_DE_FALSO: tuple[str, ...] = (
    r"\bé\s*#?\s*fake\s+que\b",
    r"\bé\s+falso\s+que\b",
    r"\bé\s+mentira\s+que\b",
    r"\bnão\s+é\s+verdade\s+que\b",
    r"\bé\s+boato\s+que\b",
    r"\bé\s+montagem\b",
    r"\bao\s+contrário\s+do\s+que\b",
)

#: Fórmulas que abrem uma checagem com veredito **verdadeiro**.
PADROES_DE_VERDADEIRO: tuple[str, ...] = (
    r"\bé\s*#?\s*fato\b",
    r"\bé\s+verdade\s+que\b",
)

#: Fração do vocabulário de conteúdo da alegação checada que precisa aparecer também no
#: texto do usuário.
SOBREPOSICAO_MINIMA = 0.5

#: Mínimo absoluto de palavras em comum. Sem ele, "é falso que Lula votou" casaria com
#: qualquer texto que mencionasse Lula.
PALAVRAS_EM_COMUM_MINIMAS = 3

#: Marcas de negação. O formato mais comum de manchete de checagem brasileira não usa
#: fórmula nenhuma — nega direto: "Lula **não** jogou bandeira do Brasil no chão após
#: votar, mas sim a entregou a fotógrafo". Sem reconhecer isso, essas manchetes entravam
#: em S-11 como "veículo publicou o mesmo fato" e iam para a N4, que leu a alegação
#: dentro do título e respondeu que a evidência a sustentava.
_NEGACOES = (
    r"\bnao\b",
    r"\bnem\b",
    r"\bnenhum[ao]?\b",
    r"\bjamais\b",
    r"\bsem\s+provas?\b",
)

_PALAVRA = re.compile(r"\b[\wÀ-ÿ]{4,}\b", re.UNICODE)

#: Palavras que aparecem em quase toda checagem e não ajudam a identificar o assunto.
_RUIDO = frozenset(
    {
        "apontam", "montagens", "posts", "post", "difundem", "real", "video",
        "imagem", "imagens", "redes", "sociais", "circula", "circulam", "afirma",
        "afirmam", "dizem", "dizendo", "sobre", "contra", "apos", "ainda", "mesmo",
        "falso", "fake", "fato", "verdade", "mentira", "boato", "montagem",
        "checagem", "verificacao",
    }
)


@dataclass(frozen=True)
class ChecagemDeAgencia:
    """Veredito encontrado numa publicação de agência."""

    #: ``"falso"`` ou ``"verdadeiro"``, no vocabulário que ``business_rules`` espera.
    veredito: str
    #: Domínio da agência, para a Vera citar a fonte como RN-01 exige.
    agencia: str
    titulo: str


def _sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def _conteudo(texto: str) -> set[str]:
    """Vocabulário de conteúdo: palavras longas, sem acento e sem o ruído de checagem."""
    return {
        palavra
        for palavra in _PALAVRA.findall(_sem_acento(texto))
        if palavra not in _RUIDO
    }


def _tem_negacao(texto: str) -> bool:
    baixo = _sem_acento(texto)
    return any(re.search(padrao, baixo) for padrao in _NEGACOES)


def nega_a_alegacao(titulo: str, texto_do_usuario: str) -> bool:
    """O título nega o que o texto do usuário afirma?

    A trava importante é a segunda condição: se a própria alegação do usuário já é
    negativa — "Lula **não** jogou a bandeira" —, um título negativo está *concordando*
    com ela, e tratar isso como desmentido inverteria o veredito.
    """
    if not _tem_negacao(titulo) or _tem_negacao(texto_do_usuario):
        return False
    return trata_da_mesma_alegacao(titulo, texto_do_usuario)


def veredito_no_titulo(titulo: str) -> str | None:
    """``"falso"``, ``"verdadeiro"`` ou ``None`` se o título não traz veredito.

    Falso é testado antes: "não é verdade que" contém "é verdade que", e ler o segundo
    inverteria o veredito da checagem — o erro mais caro que este módulo pode cometer.
    """
    baixo = titulo.lower()
    for padrao in PADROES_DE_FALSO:
        if re.search(padrao, baixo):
            return "falso"
    for padrao in PADROES_DE_VERDADEIRO:
        if re.search(padrao, baixo):
            return "verdadeiro"
    return None


def trata_da_mesma_alegacao(titulo: str, texto_do_usuario: str) -> bool:
    """O título da checagem e o texto do usuário falam do mesmo fato?

    A trava que impede o veredito de uma checagem vazar para outra alegação só porque
    as duas citam a mesma pessoa.
    """
    da_checagem = _conteudo(titulo)
    if not da_checagem:
        return False
    em_comum = da_checagem & _conteudo(texto_do_usuario)
    if len(em_comum) < PALAVRAS_EM_COMUM_MINIMAS:
        return False
    return len(em_comum) / len(da_checagem) >= SOBREPOSICAO_MINIMA


def e_checagem_desta_alegacao(titulo: str, texto_do_usuario: str) -> bool:
    """O título é uma checagem publicada **sobre esta alegação**?

    Serve para a N3 separar checagem de cobertura. Uma matéria que desmente a alegação
    não é um veículo "publicando o mesmo fato": contá-la em S-11 fazia a Vera narrar
    "5 veículos confiáveis publicaram o mesmo fato" logo abaixo de "o G1 já desmentiu
    esta alegação", e as duas frases se contradizem na cara do usuário.

    Pior: mandada à N4 como evidência, a manchete "É #FAKE que <alegação>" contém a
    alegação inteira, e o modelo respondeu ENTAILMENT para as cinco. S-12 — peso 20, o
    sinal mais pesado — declarou que **o desmentido sustentava a alegação**. Medido: sem
    RN-01 segurando, a alegação desmentida sairia com 76% de veracidade.
    """
    if veredito_no_titulo(titulo) is not None and trata_da_mesma_alegacao(
        titulo, texto_do_usuario
    ):
        return True
    return nega_a_alegacao(titulo, texto_do_usuario)


def encontrar(
    texto_do_usuario: str,
    publicacoes: list[tuple[str, str]],
) -> ChecagemDeAgencia | None:
    """Procura, entre as publicações, uma checagem de agência sobre esta alegação.

    ``publicacoes`` é uma lista de ``(domínio, título)``. Devolve a primeira checagem
    cujo título traga veredito **e** trate da mesma alegação; a ordem da lista é a do
    ranking do buscador, então a primeira é a mais relevante.
    """
    for dominio, titulo in publicacoes:
        if not titulo:
            continue
        veredito = veredito_no_titulo(titulo)
        if veredito is None:
            continue
        if not trata_da_mesma_alegacao(titulo, texto_do_usuario):
            continue
        return ChecagemDeAgencia(veredito=veredito, agencia=dominio, titulo=titulo)
    return None
