"""Triagem da entrada: isto é uma alegação para checar, ou é conversa? (RF-01, RF-02)

A Vera é um chat, então recebe "oi, tudo bem?" com a mesma frequência com que recebe
notícia. Sem esta etapa, o pipeline tratava a saudação como alegação de fato: media
estilo, saía buscar notícias semelhantes no GDELT, chamava a LLM e devolvia **77% de
veracidade** para um "Oi, tudo bem?". Além de errado, era caro — cada saudação gastava
uma busca externa e uma chamada de modelo.

A triagem roda **antes** da corrente de camadas, e não como uma camada, por dois
motivos. Ela não mede sinal nenhum, então não teria o que registrar; e a N0 do desenho
é o cache (RN-09), que é issue de outra pessoa — misturar as duas responsabilidades no
mesmo lugar geraria conflito de merge sem necessidade.

## Como ela decide

Por marcadores, não por modelo: é a etapa mais barata do produto e precisa continuar
sendo. A entrada só é tratada como conversa quando traz marca de conversa **e** não traz
nenhuma marca de alegação. Essa segunda condição é o que protege o caso que importa —
"bom dia, essa notícia do Pix é verdade?" começa com saudação e é uma checagem de
verdade, então vai para o pipeline.
"""

import re
from enum import Enum

#: Acima deste tamanho a entrada é tratada como alegação mesmo sem marca de alegação:
#: ninguém escreve dois parágrafos de conversa fiada para um checador de notícias.
LIMITE_DE_PALAVRAS_DE_CONVERSA = 25


class Natureza(str, Enum):
    """O que o usuário mandou. Só ``ALEGACAO`` entra no pipeline de checagem."""

    SAUDACAO = "saudacao"
    CONVERSA = "conversa"
    AGRADECIMENTO = "agradecimento"
    #: Pergunta sobre o resultado que a Vera **acabou de entregar** (RF-04).
    ACOMPANHAMENTO = "acompanhamento"
    ALEGACAO = "alegacao"


_SAUDACOES = (
    "oi", "olá", "ola", "oie", "bom dia", "boa tarde", "boa noite", "e aí", "e ai",
    "fala vera", "alô", "alo", "opa", "eae", "eaí", "salve",
)

_CONVERSA = (
    "tudo bem", "tudo bom", "como vai", "como você está", "como voce esta",
    "como vai você", "quem é você", "quem e voce", "o que você faz",
    "o que voce faz", "você é", "voce e", "me ajuda", "pode me ajudar",
    "pode ajudar", "qual seu nome", "qual é o seu nome", "você existe",
    "voce existe", "beleza", "de boa", "tá aí", "ta ai", "você está aí",
    "voce esta ai", "bora", "teste", "testando",
)

_AGRADECIMENTOS = (
    "obrigado", "obrigada", "obrigadão", "valeu", "vlw", "brigado", "brigada",
    "agradeço", "muito obrigado", "muito obrigada", "tchau", "até logo", "ate logo",
)

#: Pedido explícito de checagem. Conta como marca de **alegação**: quem pergunta "isso é
#: verdade?" está mandando conteúdo para checar, mesmo que cumprimente antes.
_PEDIDO_DE_CHECAGEM = (
    "é verdade", "e verdade", "é fake", "e fake", "é mentira", "e mentira",
    "procede", "confere", "checa", "cheque", "verifica", "verifique",
    "isso é real", "isso e real", "será que é", "sera que e",
)

#: Marcas de que há uma afirmação sobre o mundo no texto.
_VERBOS_DE_ALEGACAO = (
    "afirma", "afirmou", "confirma", "confirmou", "revela", "revelou", "anuncia",
    "anunciou", "divulga", "divulgou", "declara", "declarou", "aprova", "aprovou",
    "proíbe", "proibiu", "morreu", "venceu", "segundo", "de acordo com", "estudo",
    "pesquisa", "governo", "ministério", "ministerio", "presidente", "prefeito",
    "vacina", "lei", "imposto",
)

_URL = re.compile(r"https?://\S+|www\.\S+")
#: Número com dígito: data, porcentagem, valor. Alegação de fato quase sempre traz um.
_NUMERO = re.compile(r"\d")
_PALAVRA = re.compile(r"\b[\wÀ-ÿ]+\b", re.UNICODE)
_PONTUACAO_DE_BORDA = re.compile(r"^[\W_]+|[\W_]+$", re.UNICODE)


def _tem_algum(texto: str, termos: tuple[str, ...]) -> bool:
    return any(termo in texto for termo in termos)


def e_pergunta_de_acompanhamento(texto: str) -> bool:
    """A pessoa está perguntando sobre o resultado que acabou de receber?

    Reaproveita o reconhecedor de temas de :mod:`follow_up`, que é quem sabe responder
    essas perguntas: se ele não reconhece o tema, não há o que acompanhar, e tratar a
    entrada como acompanhamento só produziria "ainda não sei responder direito".
    """
    from src.core.engine.follow_up import Assunto, identificar_assunto

    return identificar_assunto(texto) is not Assunto.GERAL


def _comeca_com_saudacao(texto: str) -> bool:
    """Saudação tem de abrir a frase: "oi" solto no meio de uma notícia não conta."""
    inicio = texto[:20]
    return any(inicio.startswith(s) for s in _SAUDACOES)


def marcas_de_alegacao(texto: str) -> int:
    """Quantos indícios de que existe uma afirmação sobre o mundo a checar."""
    baixo = texto.lower()
    return sum(
        (
            bool(_URL.search(texto)),
            bool(_NUMERO.search(texto)),
            _tem_algum(baixo, _PEDIDO_DE_CHECAGEM),
            _tem_algum(baixo, _VERBOS_DE_ALEGACAO),
        )
    )


def classificar(texto: str, tem_checagem_anterior: bool = False) -> Natureza:
    """Decide o que fazer com a entrada: conversar, acompanhar ou checar.

    ``tem_checagem_anterior`` diz se já existe um resultado na tela sobre o qual a
    pessoa possa estar perguntando. Sem ele, "por que você achou isso?" é uma alegação
    sem pé nem cabeça; com ele, é a pergunta de acompanhamento de RF-04.

    Na dúvida devolve :attr:`Natureza.ALEGACAO`. O erro de checar uma conversa custa
    uma resposta estranha; o erro de **não** checar custa deixar o usuário sem a
    resposta que ele veio buscar — então o viés é para checar.

    Esta função é a única fonte da decisão. A interface não pode adivinhar por conta
    própria: ela tentava, pelo número de palavras, e mandava para o acompanhamento toda
    alegação com menos de 25 palavras — de modo que, depois da primeira checagem, cada
    notícia curta recebia "essa sua pergunta eu ainda não sei responder direito".
    """
    limpo = _PONTUACAO_DE_BORDA.sub("", texto.strip()).lower()
    if not limpo:
        return Natureza.CONVERSA

    palavras = _PALAVRA.findall(limpo)
    if len(palavras) > LIMITE_DE_PALAVRAS_DE_CONVERSA:
        return Natureza.ALEGACAO

    tem_marca_de_alegacao = marcas_de_alegacao(texto) > 0

    # Pergunta sobre o resultado anterior: tem tema reconhecido e **nada** que pareça
    # uma afirmação nova. A segunda condição é o que separa "por que você achou isso?"
    # de "por que o governo vai taxar o Pix em 15%?", que é alegação a checar.
    if (
        tem_checagem_anterior
        and not tem_marca_de_alegacao
        and e_pergunta_de_acompanhamento(texto)
    ):
        return Natureza.ACOMPANHAMENTO

    if tem_marca_de_alegacao:
        return Natureza.ALEGACAO

    if _tem_algum(limpo, _AGRADECIMENTOS):
        return Natureza.AGRADECIMENTO
    if _tem_algum(limpo, _CONVERSA):
        return Natureza.CONVERSA
    if _comeca_com_saudacao(limpo):
        return Natureza.SAUDACAO

    # Texto curtíssimo sem nada que pareça afirmação: "aham", "kkkk", "?".
    if len(palavras) <= 2:
        return Natureza.CONVERSA

    return Natureza.ALEGACAO


#: Resposta da Vera para cada tipo de conversa. Uma marca regional por frase, e todas
#: terminam convidando a pessoa a mandar o que ela quer conferir — a conversa serve para
#: chegar na checagem, não para substituí-la (ver a skill ``vera-voz``).
RESPOSTAS: dict[Natureza, str] = {
    Natureza.SAUDACAO: (
        "Oi, meu bem! Senta aqui. Me manda a notícia que tu quer conferir que eu "
        "vou atrás."
    ),
    Natureza.CONVERSA: (
        "Eu tô bem, meu bem, obrigada por perguntar. Eu sou a Vera, e o que eu faço "
        "é conferir notícia: tu me manda o texto ou o link e eu te mostro quem "
        "publicou, o que eu achei e o quanto cada coisa pesou. Manda ver."
    ),
    Natureza.AGRADECIMENTO: (
        "Que isso, parêia, imagina. Quando aparecer outra dessas, me manda que eu "
        "confiro, visse?"
    ),
}


def resposta_para(natureza: Natureza) -> str:
    """A fala da Vera para uma entrada que não é checagem."""
    return RESPOSTAS.get(natureza, RESPOSTAS[Natureza.CONVERSA])
