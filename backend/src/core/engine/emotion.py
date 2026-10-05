"""Intensidade emocional manipulativa, medida pela camada N2 (RF-23, S-08).

## O que este sinal mede, e o que ele deliberadamente não mede

Mede **vocabulário de degradação moral**: chamar alguém de bandido, vagabundo, canalha,
verme. É o registro em que a desinformação fala, porque o objetivo dela é produzir
indignação, não informar.

Não mede assunto triste. A versão anterior deste módulo tratava "morte", "crise",
"risco", "doença" e "guerra" como carga emocional, e a medição contra 15.854 textos
rotulados dos datasets do projeto mostrou que essas palavras aparecem de **duas a quatro
vezes mais em notícia verdadeira** do que em falsa (``crise`` lift 0,27; ``doença``
0,27; ``risco`` 0,29; ``morte`` 0,50). O sinal estava detectando jornalismo sério sobre
notícia ruim e punindo por isso: a AUC dava 0,39 — abaixo de 0,5, isto é, apontando para
o lado errado. Uma matéria do Ministério da Saúde sobre dengue zerava S-08.

Cada palavra deste léxico foi validada contra aqueles mesmos datasets e só ficou se
aparece ao menos 1,3 vez mais em texto falso (o *lift* medido está anotado em cada
entrada). Termos de identidade política saíram da lista mesmo com lift alto: por RN-08
viés político é contexto e não altera o score, então "comunista" e "esquerdista", que a
mineração trouxe com lift 3,6 e 7,7, seriam uma violação direta da regra.

## Por que ele fica indisponível na maior parte das vezes

O léxico dispara em 8,9% dos textos. Quando dispara, a densidade separa falso de
verdadeiro com **AUC 0,806** e a chance de o texto ser falso sobe de 49% para 67%.
Quando não dispara, não há nada medido — e por RN-06 o sinal sai do cálculo em vez de
valer 1,0. Essa diferença é o conserto principal: antes, ausência de insulto era somada
como evidência de veracidade, e por isso "Oi, tudo bem?" pontuava 77% de veracidade.
"""

import re
from collections import Counter

#: Léxico de degradação moral, no espírito do NRC Emotion Lexicon mas calibrado nos
#: corpora brasileiros do projeto. O número é o *lift* medido: quantas vezes mais a
#: palavra aparece em texto falso do que em verdadeiro.
LEXICO_EMOCIONAL_PT: dict[str, str] = {
    # Raiva — desqualificação da pessoa, não do argumento.
    "vagabundos": "raiva",   # lift 7,31
    "idiotas": "raiva",      # lift 4,79
    "vagabundo": "raiva",    # lift 4,62
    "hipócrita": "raiva",    # lift 3,29
    "canalhas": "raiva",     # lift 3,08
    "hipócritas": "raiva",   # lift 2,93
    "bandido": "raiva",      # lift 2,81
    "corrupto": "raiva",     # lift 2,67
    "assassinos": "raiva",   # lift 2,59
    "corruptos": "raiva",    # lift 2,53
    "bandidos": "raiva",     # lift 2,30
    "marginais": "raiva",    # lift 2,18
    "assassino": "raiva",    # lift 2,12
    "ladrão": "raiva",       # lift 2,11
    "safado": "raiva",       # lift 2,05
    "imbecil": "raiva",      # lift 1,85
    "ladrões": "raiva",      # lift 1,58
    "mentiroso": "raiva",    # lift 1,52
    "idiota": "raiva",       # lift 1,51
    "canalha": "raiva",      # lift 1,43
    # Nojo — desumanização.
    "podre": "nojo",         # lift 4,39
    "nojenta": "nojo",       # lift 3,52
    "vermes": "nojo",        # lift 3,08
    "vergonhoso": "nojo",    # lift 2,31
    "sujeira": "nojo",       # lift 1,92
    "nojo": "nojo",          # lift 1,91
    # Medo.
    "assustador": "medo",    # lift 1,69
}

#: Densidade de palavras do léxico a partir da qual o índice satura em 1,0.
#:
#: 2% vem do levantamento nos cinco datasets: entre os textos em que o léxico dispara,
#: este valor dá a melhor separação (AUC 0,805) deixando só 20,8% dos casos no teto — o
#: que preserva gradiente na explicação. O valor anterior, 3% sobre o léxico antigo,
#: saturava com **uma única** palavra num texto de 33, então quase toda medição virava
#: "carga emocional intensa (100%)" e a justificativa não informava nada.
SATURACAO_DE_DENSIDADE = 0.02

_PALAVRA = re.compile(r"\b[\wÀ-ÿ]+\b", re.UNICODE)


def analisar_emocoes(texto: str) -> dict[str, int]:
    """Conta quantas palavras de cada emoção o texto traz."""
    palavras = _PALAVRA.findall(texto.lower())
    contagem: Counter[str] = Counter()
    for palavra in palavras:
        emocao = LEXICO_EMOCIONAL_PT.get(palavra)
        if emocao is not None:
            contagem[emocao] += 1
    return dict(contagem)


def indice_intensidade_emocional(texto: str) -> tuple[float | None, str]:
    """Densidade de vocabulário manipulativo, de 0 a 1, e a emoção predominante.

    Devolve ``(None, "")`` quando o texto não traz nenhuma palavra do léxico. Isso é
    diferente de devolver ``(0.0, "")``: por RN-06 a camada traduz o ``None`` em sinal
    indisponível, que derruba a cobertura, enquanto um zero seria lido como "medi e está
    limpo" e somaria veracidade a qualquer texto sem insulto — inclusive a um "bom dia".
    """
    palavras = _PALAVRA.findall(texto.lower())
    if not palavras:
        return None, ""

    contagem = analisar_emocoes(texto)
    total_emocionais = sum(contagem.values())
    if total_emocionais == 0:
        return None, ""

    densidade = total_emocionais / len(palavras)
    indice = min(1.0, densidade / SATURACAO_DE_DENSIDADE)
    emocao_predominante = max(contagem.items(), key=lambda item: item[1])[0]
    return indice, emocao_predominante
