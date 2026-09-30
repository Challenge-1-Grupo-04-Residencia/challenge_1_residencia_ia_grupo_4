import re

_URGENCIA = (
    "urgente",
    "repassem",
    "repasse",
    "compartilhe",
    "compartilhem",
    "acordem",
    "antes que apaguem",
    "a mídia não mostra",
    "a midia nao mostra",
    "não vão te contar",
    "nao vao te contar",
    "última hora",
    "ultima hora",
    "bomba",
    "chocante",
    "você não vai acreditar",
    "voce nao vai acreditar",
)

# _URGENTE: é uma tupla que contem palavras-chave comuns em mensagens alarmistas ou correntes falsas de WhatsApp

_PALAVRA = re.compile(r"\b[\wÀ-ÿ]+\b", re.UNICODE)
# _PALAVRA: Separa apenas as palavras reais do texto, jogando fora espaços, pontos e vírgulas para a análise funcionar direito.
_URL = re.compile(r"https?://\S+")
# _URL: serve para encontrar links na web

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

 #FONTES_NOMEADAS: Serve para identificar quando o texto tenta dar credibilidade citando órgãos oficiais

def indice_sensacionalismo(texto: str) -> float:

    palavras = _PALAVRA.findall(texto)
    if not palavras:
        return 0.0

    # ETAPA 1: Usa _PALAVRAS para separar todas as palavras e 
    # checa se o texto está vazio (se estiver, devolve nota 0 direto).

    longas = [p for p in palavras if len(p) >= 3]
    caixa_alta = sum(1 for p in longas if p.isupper()) / len(longas) if longas else 0.0

    # ETAPA 2: Teste do Grito. Filtra palavras com 3+ letras 
    # (ignorando siglas) e calcula quantas estão totalmente em CAIXA ALTA.

    repetida = len(re.findall(r"[!?]{2,}", texto))
    pontuacao = min(1.0, repetida / max(1, len(palavras) / 100) / 3)

    # ETAPA 3: Teste da Pontuação. Conta repetições exageradas 
    # de exclamações ou interrogações (como "!!!") e ajusta pelo tamanho do texto.

    baixo = texto.lower()
    urgencia = min(1.0, sum(1 for termo in _URGENCIA if termo in baixo) / 3)

    # ETAPA 4: Teste do Pânico. Transforma o texto em letras minúsculas 
    # e conta quantas palavras de urgência (da tupla _URGENCIA) aparecem nele.

    return min(1.0, (caixa_alta + pontuacao + urgencia) / 3)

    # ETAPA 5: Junta os três testes (caixa alta, pontuação e urgência), 
    # tira a média deles e devolve um número final de 0 a 1.

def indice_citacao_de_fontes(texto: str) -> float:

    baixo = texto.lower()

    # ETAPA 1: Converte o texto inteiro para letras minúsculas 
    # para garantir que a busca encontre os nomes dos órgãos, independentemente de como foram digitados.

    links = len(_URL.findall(texto))

    # ETAPA 2: Usa a ferramenta de busca de links (_URL) 
    # para contar quantas referências da web existem no texto.

    nomeadas = sum(1 for f in _FONTES_NOMEADAS if f in baixo)

    # ETAPA 3: Passa pela tupla _FONTES_NOMEADAS e conta 
    # quantas menções a órgãos oficiais ou termos de pesquisa confiáveis aparecem no texto.

    return min(1.0, (links + nomeadas) / 3)

    # ETAPA 4: Soma os links e as menções encontradas, 
    # divide por 3 (já que 3 ou mais citações tornam o texto bem ancorado) e limita a nota final até o teto de 1.0.