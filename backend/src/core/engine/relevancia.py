"""Relevância textual entre a alegação e um documento recuperado (RF-27, issue #73).

A N3 recupera candidatos por palavra-chave, e buscadores como o Google Notícias não
expõem score de relevância — a similaridade deles é derivada da posição no ranking, que
não diz se o documento é *sobre a mesma coisa*. Resultado: "lula vai taxar o pix" casava
com "taxa das blusinhas", e esse documento chegava à N4 como se fosse evidência.

Este módulo mede, sem rede e sem modelo pesado, o quanto um título **compartilha de
conteúdo** com a alegação: cosseno entre os vetores de frequência das palavras de
conteúdo (ignorando palavras de função e acento). É uma medida honesta de sobreposição
lexical — não resolve sinônimo nem papel semântico (isso é trabalho da N4), mas é o
bastante para barrar o documento que só divide o assunto geral.
"""

import math
import re
import unicodedata
from collections import Counter

#: Palavras de função: não carregam o assunto, então não contam para a sobreposição.
_VAZIAS = frozenset(
    """
    a o os as um uma uns umas de do da dos das em no na nos nas por pelo pela pelos
    pelas com sem sob sobre ao aos à às e ou mas que se como quando onde porque pra
    para por entre até desde após antes depois este esta isto esse essa isso aquele
    aquela aquilo seu sua seus suas meu minha teu tua nosso nossa dele dela deles delas
    eu tu ele ela nos vos eles elas voce vocês me te lhe nos vos lhes isso aqui ali
    vai vão foi ser sera são é era eram tem têm ter há mais menos muito pouco já não
    sim também só apenas cada todo toda todos todas qualquer outro outra do
    """.split()
)

_PALAVRA = re.compile(r"[0-9a-zà-ÿ]+", re.IGNORECASE)


def _normalizar(texto: str) -> list[str]:
    """Minúsculas, sem acento, só palavras de conteúdo com 2+ caracteres."""
    sem_acento = "".join(
        c
        for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )
    return [
        p
        for p in _PALAVRA.findall(sem_acento)
        if len(p) >= 2 and p not in _VAZIAS
    ]


def relevancia(alegacao: str, titulo: str) -> float:
    """Cosseno de frequência de termos entre a alegação e o título, de 0 a 1.

    0 quando não há palavra de conteúdo em comum; 1 quando os conjuntos de palavras
    coincidem. Textos sem nenhuma palavra de conteúdo devolvem 0.
    """
    a = Counter(_normalizar(alegacao))
    b = Counter(_normalizar(titulo))
    if not a or not b:
        return 0.0

    comuns = set(a) & set(b)
    produto = sum(a[t] * b[t] for t in comuns)
    if produto == 0:
        return 0.0

    norma_a = math.sqrt(sum(v * v for v in a.values()))
    norma_b = math.sqrt(sum(v * v for v in b.values()))
    return produto / (norma_a * norma_b)
