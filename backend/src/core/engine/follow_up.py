"""Perguntas de acompanhamento sobre um resultado já entregue (RF-04).

Responde sem refazer a checagem, usando os sinais e as evidências que a N3 já
recuperou — que é o que a história de usuário pede como contexto.

## Por que por templates, e não por LLM

A N4 chama um LLM, mas com uma tarefa fechada: julgar, por evidência, se ela sustenta
ou contradiz a alegação. Usá-la para redigir resposta aberta sobre o resultado é outro
problema, e por ora esta é a explicação em **modo econômico** descrita em
``docs/produto/funcionamento.md``: "explicação montada por templates com as frases da
Vera". Templates também custam zero e não inventam.

A troca futura é substituir :func:`responder` por uma chamada ao provedor, passando os
mesmos sinais e evidências como contexto. A forma do contexto já está pronta.

Isto tem um limite honesto: perguntas fora dos temas reconhecidos recebem uma resposta
que diz o que a Vera **sabe** sobre aquela checagem, em vez de inventar. Preferimos
admitir o alcance a fabricar uma resposta — o produto existe para sustentar pensamento
crítico, não para parecer onisciente.
"""

from dataclasses import dataclass
from enum import Enum

from src.core.engine import scoring
from src.core.entities.checagem_registrada import ChecagemRegistrada
from src.core.entities.signal import Dimensao


class Assunto(str, Enum):
    """O que a pergunta quer saber."""

    MOTIVO = "motivo"
    FONTES = "fontes"
    ESTILO = "estilo"
    CONFIANCA = "confianca"
    LACUNAS = "lacunas"
    GERAL = "geral"


#: Termos que identificam cada assunto. A ordem da varredura importa: assuntos mais
#: específicos são testados antes de "motivo", que é o mais genérico.
_TERMOS: tuple[tuple[Assunto, tuple[str, ...]], ...] = (
    (
        Assunto.FONTES,
        ("fonte", "fontes", "quem publicou", "onde saiu", "veiculo", "veículo",
         "jornal", "site", "link", "referencia", "referência"),
    ),
    (
        Assunto.ESTILO,
        ("estilo", "escrito", "escrita", "sensacionalis", "emocional", "linguagem",
         "texto", "palavras", "clickbait"),
    ),
    (
        Assunto.CONFIANCA,
        ("confian", "certeza", "seguro", "segura", "tem certeza", "quanto voce sabe",
         "quanto você sabe", "cobertura"),
    ),
    (
        Assunto.LACUNAS,
        ("falta", "faltou", "nao sabe", "não sabe", "nao soube", "não soube",
         "o que ficou", "nao conseguiu", "não conseguiu", "inconclusiv"),
    ),
    (
        Assunto.MOTIVO,
        ("por que", "porque", "porquê", "por quê", "como voce", "como você",
         "chegou", "motivo", "razao", "razão", "explica", "baseou"),
    ),
)


@dataclass(frozen=True)
class FonteCitada:
    """Uma publicação citada na resposta, com o que o usuário precisa para conferir.

    Só a URL não basta: o buscador devolve link de redirecionador, e uma lista de
    endereços opacos de 500 caracteres não deixa ninguém ver quem publicou.
    """

    titulo: str
    url: str
    veiculo: str
    confiavel: bool


@dataclass(frozen=True)
class Resposta:
    """Resposta a uma pergunta de acompanhamento."""

    texto: str
    assunto: Assunto
    #: Publicações citadas na resposta, para a interface poder linká-las (RN-05).
    fontes: list[FonteCitada]
    #: IDs dos sinais em que a resposta se apoia, para auditoria (RF-33).
    sinais_citados: list[str]


def identificar_assunto(pergunta: str) -> Assunto:
    """Classifica a pergunta por palavras-chave."""
    baixo = pergunta.lower()
    for assunto, termos in _TERMOS:
        if any(termo in baixo for termo in termos):
            return assunto
    return Assunto.GERAL


def responder(pergunta: str, checagem: ChecagemRegistrada) -> Resposta:
    """Responde sobre uma checagem já concluída, na voz da Vera."""
    assunto = identificar_assunto(pergunta)

    if assunto is Assunto.FONTES:
        return _sobre_fontes(checagem)
    if assunto is Assunto.ESTILO:
        return _sobre_estilo(checagem)
    if assunto is Assunto.CONFIANCA:
        return _sobre_confianca(checagem)
    if assunto is Assunto.LACUNAS:
        return _sobre_lacunas(checagem)
    if assunto is Assunto.MOTIVO:
        return _sobre_motivo(checagem)
    return _resposta_geral(checagem)


def _fontes_de(checagem: ChecagemRegistrada) -> list[FonteCitada]:
    """Converte as publicações guardadas em algo clicável e identificável."""
    return [
        FonteCitada(
            titulo=documento.titulo or documento.fonte or "publicação sem título",
            url=documento.url,
            veiculo=documento.fonte,
            confiavel=documento.fonte_confiavel,
        )
        for documento in checagem.documentos_relacionados
        if documento.url
    ]


def _sobre_fontes(checagem: ChecagemRegistrada) -> Resposta:
    if not checagem.fontes_citadas:
        texto = (
            "Pois é, meu bem: nessa eu não achei outra publicação falando do mesmo "
            "assunto. Não quer dizer que seja mentira — pode ser notícia muito nova ou "
            "de um assunto bem específico —, mas é por isso que eu não cravei."
        )
        return Resposta(texto, Assunto.FONTES, [], ["S-11"])

    fontes = _fontes_de(checagem)
    quantas = len(fontes) or len(checagem.fontes_citadas)
    plural = "publicações" if quantas > 1 else "publicação"
    texto = (
        f"Olha, eu fui conferir com as comadres e achei {quantas} {plural} sobre isso. "
        "Tá tudo aí embaixo pra você clicar e ler com seus próprios olhos — não precisa "
        "acreditar em mim, não."
    )
    return Resposta(texto, Assunto.FONTES, fontes, ["S-11"])


def _sobre_estilo(checagem: ChecagemRegistrada) -> Resposta:
    do_conteudo = [
        s
        for s in checagem.sinais
        if s.dimensao is Dimensao.CONTEUDO and s.disponivel
    ]
    if not do_conteudo:
        return Resposta(
            "Nessa eu não cheguei a analisar o jeito que o texto foi escrito.",
            Assunto.ESTILO,
            [],
            [],
        )

    partes = [s.justificativa for s in do_conteudo if s.justificativa]
    corpo = " ".join(partes) if partes else "Analisei o jeito que o texto foi escrito."
    texto = f"Sobre o jeito que isso foi escrito: {corpo}"
    return Resposta(texto, Assunto.ESTILO, [], [s.id for s in do_conteudo])


def _sobre_confianca(checagem: ChecagemRegistrada) -> Resposta:
    medidos = [s for s in checagem.sinais if s.disponivel]
    # Só lacuna de verdade conta como "faltou": o detector que rodou e não achou nada
    # não é coisa que a Vera deixou de apurar. Contá-lo fazia a resposta dizer que
    # faltaram sinais justamente nas notícias em que tudo foi olhado.
    faltando = [s for s in checagem.sinais if s.e_lacuna]
    peso_medido = sum(s.peso for s in medidos)

    texto = (
        f"Eu consegui medir {len(medidos)} coisa(s) sobre essa notícia, o que dá "
        f"{peso_medido:.0f} de 100 pontos do que eu costumo olhar. "
    )
    if faltando:
        texto += (
            f"Faltaram {len(faltando)}, e é por isso que eu não fico mais convicta. "
        )
    texto += (
        "Quanto menos eu consigo apurar, mais eu seguro a língua — prefiro dizer que "
        "não sei do que te dar uma certeza que eu não tenho."
    )
    return Resposta(texto, Assunto.CONFIANCA, [], [s.id for s in medidos])


def _sobre_lacunas(checagem: ChecagemRegistrada) -> Resposta:
    faltando = [s for s in checagem.sinais if s.e_lacuna]
    if not faltando:
        return Resposta(
            "Nessa eu consegui apurar tudo o que costumo olhar, viu?",
            Assunto.LACUNAS,
            [],
            [],
        )

    nomes = ", ".join(s.nome.lower() for s in faltando[:3])
    texto = (
        f"O que me faltou foi: {nomes}. "
        "Sinal que eu não consigo medir eu deixo de fora da conta — não conto como "
        "ponto contra a notícia, só reconheço que não sei."
    )
    return Resposta(texto, Assunto.LACUNAS, [], [s.id for s in faltando])


def _sobre_motivo(checagem: ChecagemRegistrada) -> Resposta:
    if checagem.regra_aplicada and checagem.explicacao:
        return Resposta(
            checagem.explicacao.strip(),
            Assunto.MOTIVO,
            _fontes_de(checagem),
            [],
        )

    principais = scoring.principais_sinais(checagem.sinais, limite=3)
    if not principais:
        return Resposta(
            "Nessa eu não consegui apurar quase nada, por isso não cravei.",
            Assunto.MOTIVO,
            [],
            [],
        )

    motivos = " ".join(s.justificativa for s in principais if s.justificativa)
    texto = f"O que mais pesou foi isso: {motivos}"
    return Resposta(
        texto, Assunto.MOTIVO, _fontes_de(checagem), [s.id for s in principais]
    )


def _resposta_geral(checagem: ChecagemRegistrada) -> Resposta:
    """Para perguntas fora dos temas reconhecidos.

    Diz o que a Vera sabe e oferece caminhos, em vez de inventar resposta — enquanto
    não houver um gerador de texto, fabricar seria pior do que admitir o alcance.
    """
    if checagem.exibe_porcentagem and checagem.veracidade is not None:
        abertura = (
            f"Sobre essa notícia eu cheguei em {checagem.veracidade:.0f}% de "
            f"veracidade — {checagem.faixa.lower()}."
        )
    else:
        abertura = f"Sobre essa notícia o meu veredito foi: {checagem.faixa.lower()}."

    texto = (
        f"{abertura} Essa sua pergunta eu ainda não sei responder direito, viu? "
        "Mas me pergunte por que eu cheguei nesse resultado, quais fontes eu conferi, "
        "como o texto foi escrito, ou o que me faltou apurar — dessas eu falo."
    )
    return Resposta(texto, Assunto.GERAL, [], [])
