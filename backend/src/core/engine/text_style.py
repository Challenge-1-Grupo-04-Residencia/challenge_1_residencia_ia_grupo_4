"""Marcas de estilo no texto, medidas pela camada N2: S-07 e S-09.

## Como estes dois sinais foram calibrados

Contra 15.854 textos rotulados dos cinco corpora do projeto (fake-br, FakeRecogna,
faketrue-br, fakewhatsapp-br, faketweet-br). O que a medição mostrou:

- **Caixa alta saiu da conta.** Era um terço do índice de sensacionalismo e é
  anti-preditiva: dispara em 39,7% das notícias verdadeiras contra 30,7% das falsas, e
  a chance de ser falsa *cai* para 0,43 quando ela aparece. O motivo é prosaico — o
  filtro aceitava qualquer palavra de 3+ letras em maiúsculas, então "IBGE", "STF" e
  "ONU" contavam como grito. Exigir duas palavras maiúsculas seguidas, para pegar grito
  de verdade e não sigla, também não discrimina (0,471): manchete e linha fina em caixa
  alta são comuns no jornalismo destes corpora.
- **Metade do vocabulário de urgência era ruído.** "bomba" (lift 0,87), "última hora"
  (0,78), "chocante" (0,95) e "repasse" (0,94) aparecem igualmente nos dois lados e
  foram removidos. Ficaram os que pedem difusão: "urgente" (2,66), "repassem" (2,61),
  "compartilhem" (2,36), "compartilhe" (2,13), "acordem" (26,7).
- **O que informa é o sinal disparar, não a sua intensidade.** Por número de
  marcadores: 0 → 46,5% de chance de ser falsa, 1 → 68,1%, 2 → 75,7%. Dentro da faixa
  em que dispara, a intensidade acrescenta pouco (AUC 0,51), então o índice é uma
  escala grosseira de contagem e não finge precisão que a medição não sustenta.
"""

import re

#: Pedidos de difusão e de urgência, só os que a medição aprovou (lift ≥ 1,3). Os
#: números são quantas vezes mais o termo aparece em texto falso do que em verdadeiro.
#:
#: É público porque os adaptadores de busca precisam da lista: estes termos descrevem a
#: **embalagem** da mensagem, não o assunto dela, e se entrarem na consulta engolem o
#: tema real. Medido: "URGENTE!!! REPASSEM!!! ... vacina tem grafeno" virava a consulta
#: "urgente repassem antes apaguem descobriram nova", que devolve zero resultados,
#: enquanto "vacina grafeno" devolve as checagens do G1 e do Estadão.
VOCABULARIO_DE_URGENCIA = (
    "acordem",                 # lift 26,69
    "urgente",                 # lift 2,66
    "repassem",                # lift 2,61
    "compartilhem",            # lift 2,36
    "compartilhe",             # lift 2,13
    # Abaixo: ocorrência rara demais nos corpora para medir, mantidos porque são a
    # assinatura textual de corrente de WhatsApp e o custo de um falso positivo aqui é
    # baixo — o sinal inteiro só pode descontar 5 pontos.
    "antes que apaguem",
    "a mídia não mostra",
    "a midia nao mostra",
    "não vão te contar",
    "nao vao te contar",
    "você não vai acreditar",
    "voce nao vai acreditar",
)

#: Alias interno, para o resto do módulo seguir legível.
_URGENCIA = VOCABULARIO_DE_URGENCIA

#: Separa palavras de pontuação, para a contagem não ser enganada por vírgulas e pontos.
_PALAVRA = re.compile(r"\b[\wÀ-ÿ]+\b", re.UNICODE)
_URL = re.compile(r"https?://\S+")
#: "!!!" ou "?!?" — exclamação e interrogação repetidas.
_PONTUACAO_REPETIDA = re.compile(r"[!?]{2,}")

#: Contagem de marcadores a partir da qual o índice satura. Em 4 marcadores a chance
#: medida de o texto ser falso passa de 80%.
_MARCADORES_PARA_SATURAR = 4

_FONTES_NOMEADAS = (
    "ministério",
    "ministerio",
    "ibge",
    "fiocruz",
    "anvisa",
    "oms",
    "organização mundial da saúde",
    "supremo tribunal federal",
    "stf",
    "universidade",
    "segundo o estudo",
    "de acordo com a pesquisa",
    "revista científica",
    "revista cientifica",
)


def indice_sensacionalismo(texto: str) -> float | None:
    """Intensidade das marcas de sensacionalismo, de 0 a 1.

    Devolve ``None`` quando nenhuma marca aparece. Isso é o conserto central deste
    módulo: antes, texto sem marca nenhuma recebia índice 0, que a camada convertia em
    score 1,0 e somava como evidência de veracidade. Com peso 5 e disparando em 12,5%
    dos casos, o sinal passava 87,5% do tempo empurrando *qualquer* texto para cima —
    inclusive "Oi, tudo bem?" e mentira escrita em tom sóbrio. Por RN-06, não encontrar
    marca é não ter medido nada, e o sinal sai do cálculo.
    """
    palavras = _PALAVRA.findall(texto)
    if not palavras:
        return None

    repeticoes = len(_PONTUACAO_REPETIDA.findall(texto))
    baixo = texto.lower()
    urgencia = sum(1 for termo in _URGENCIA if termo in baixo)

    marcadores = repeticoes + urgencia
    if marcadores == 0:
        return None
    return min(1.0, marcadores / _MARCADORES_PARA_SATURAR)


def indice_citacao_de_fontes(texto: str) -> float:
    """Quanto o texto ancora o que afirma em link ou órgão nomeado, de 0 a 1.

    É o único dos três heurísticos de conteúdo que mede bem nos dois sentidos: citar
    fonte verificável é evidência de prática jornalística e não citar é evidência
    contra, com AUC entre 0,53 e 0,74 nos corpora. Por isso continua simétrico, em vez
    de só poder descontar como S-07 e S-08.

    Três citações bastam para o texto ser considerado bem ancorado.
    """
    baixo = texto.lower()
    links = len(_URL.findall(texto))
    nomeadas = sum(1 for fonte in _FONTES_NOMEADAS if fonte in baixo)
    return min(1.0, (links + nomeadas) / 3)
