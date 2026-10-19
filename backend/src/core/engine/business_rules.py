"""Regras que se sobrepõem ao score calculado (RF-10).

Algumas evidências valem mais do que a média ponderada dos sinais. Uma checagem de
agência signatária da IFCN, por exemplo, é verificação humana publicada — ela decide o
veredito em vez de virar mais um sinal entre treze.

As regras são aplicadas **depois** do cálculo, sobre o resultado já pronto, e cada uma
registra em ``regra_aplicada`` por que o score publicado difere do score calculado.
"""

from dataclasses import dataclass

from src.core.engine import triagem
from src.core.engine.scoring import C_INCONCLUSIVO, Faixa, classificar


@dataclass(frozen=True)
class Veredito:
    """Resultado final, já com as regras de negócio aplicadas."""

    veracidade: float | None
    confianca: float
    faixa: Faixa
    #: ``None`` quando o score calculado prevaleceu; senão o ID da regra (ex.: "RN-01").
    regra_aplicada: str | None = None
    #: Explicação da regra, para entrar na resposta ao usuário.
    motivo_regra: str = ""
    #: RN-03: opinião e sátira não recebem porcentagem.
    exibe_porcentagem: bool = True


@dataclass(frozen=True)
class Contexto:
    """Fatos sobre a checagem que ativam regras, coletados pelas camadas."""

    #: RN-01 — veredito de agência signatária da IFCN, se houver ("falso"/"verdadeiro").
    veredito_agencia: str | None = None
    agencia: str | None = None
    #: RN-02 — o domínio imita um veículo conhecido (typosquatting)?
    dominio_impostor: bool = False
    veiculo_imitado: str | None = None
    #: RN-03 — natureza do conteúdo: ``opiniao``, ``satira``, ou um dos valores de
    #: :class:`triagem.Natureza` quando a entrada não era alegação de fato.
    natureza: str | None = None
    #: A checagem já passou por todas as camadas? RN-04 só vale no fim do pipeline.
    pipeline_encerrado: bool = False
    #: Quantos veículos confiáveis **independentes** corroboraram o fato (cobertura, não
    #: checagem). Confirmar uma notícia exige mais de um: o valor do produto está em
    #: várias redações independentes baterem, e um modelo pequeno dizendo "procede" com
    #: base num único veículo vira fake aprovada.
    apoios_independentes: int = 0


def aplicar(
    veracidade: float | None,
    confianca: float,
    contexto: Contexto,
) -> Veredito:
    """Aplica as regras em ordem de precedência e devolve o veredito publicável.

    A ordem importa: uma checagem de agência (RN-01) vence o alerta de impostor
    (RN-02), porque a agência já avaliou o conteúdo concreto, e ambas vencem o corte de
    confiança (RN-04), que só existe para o caso em que nada decisivo foi encontrado.
    """
    # Antes de tudo: a entrada era uma alegação de fato? Saudação, conversa e
    # agradecimento não são checagem, então não recebem veredito nenhum. Sem esta
    # guarda, "Oi, tudo bem?" saía com 77% de veracidade (ver ``triagem``).
    naturezas_de_conversa = {
        triagem.Natureza.SAUDACAO.value,
        triagem.Natureza.CONVERSA.value,
        triagem.Natureza.AGRADECIMENTO.value,
    }
    if contexto.natureza in naturezas_de_conversa:
        return Veredito(
            veracidade=None,
            confianca=0.0,
            faixa=Faixa.CONVERSA,
            regra_aplicada="TRIAGEM",
            motivo_regra=triagem.resposta_para(
                triagem.Natureza(contexto.natureza)
            ),
            exibe_porcentagem=False,
        )

    # RN-03 — opinião e sátira não são alegações de fato: não recebem porcentagem.
    if contexto.natureza in ("opiniao", "satira"):
        rotulo = "opinião" if contexto.natureza == "opiniao" else "sátira"
        return Veredito(
            veracidade=None,
            confianca=confianca,
            faixa=Faixa.INCONCLUSIVA,
            regra_aplicada="RN-03",
            motivo_regra=(
                f"Este conteúdo é {rotulo}, não uma alegação de fato — "
                "por isso não recebe porcentagem de veracidade."
            ),
            exibe_porcentagem=False,
        )

    # RN-01 — o veredito da agência prevalece sobre o score calculado.
    if contexto.veredito_agencia is not None:
        agencia_raw = (contexto.agencia or "uma agência signatária da IFCN").strip()
        mapa_agencias = {
            "lupa": "Agência Lupa",
            "aos fatos": "Aos Fatos",
            "fato-ou-fake": "Fato ou Fake (G1)",
            "boatos": "Boatos.org",
            "estadao_verifica": "Estadão Verifica",
            "comprova": "Projeto Comprova",
        }
        agencia = mapa_agencias.get(
            agencia_raw.lower(),
            agencia_raw.title() if agencia_raw.islower() else agencia_raw,
        )

        if contexto.veredito_agencia == "falso":
            v = 10.0
            motivo = f"{agencia} já verificou esta alegação e a desmentiu como falsa (chance altíssima de falsidade)."
        else:
            v = 90.0
            motivo = f"{agencia} já verificou esta alegação oficialmente e confirmou os fatos (chance altíssima de ser verdadeira)."
        return Veredito(
            veracidade=v,
            confianca=max(confianca, C_INCONCLUSIVO),
            faixa=classificar(v),
            regra_aplicada="RN-01",
            motivo_regra=motivo,
        )

    # RN-02 — domínio que imita veículo conhecido é teto duro de 15.
    if contexto.dominio_impostor:
        v = min(15.0, veracidade if veracidade is not None else 15.0)
        imitado = contexto.veiculo_imitado or "um veículo conhecido"
        return Veredito(
            veracidade=v,
            confianca=confianca,
            faixa=classificar(v),
            regra_aplicada="RN-02",
            motivo_regra=(
                f"Atenção: este domínio imita o endereço de {imitado}. "
                "É um site impostor."
            ),
        )

    # RN-04 — sem confiança ao fim do pipeline, o resultado é Inconclusivo.
    if contexto.pipeline_encerrado and confianca < C_INCONCLUSIVO:
        return Veredito(
            veracidade=veracidade,
            confianca=confianca,
            faixa=Faixa.INCONCLUSIVA,
            regra_aplicada="RN-04",
            motivo_regra=(
                "Não encontrei informações confiáveis suficientes na internet para confirmar ou desmentir "
                "isso com segurança. Na dúvida, o melhor é não compartilhar."
            ),
            exibe_porcentagem=False,
        )

    if veracidade is None:
        return Veredito(
            veracidade=None,
            confianca=confianca,
            faixa=Faixa.INCONCLUSIVA,
            regra_aplicada="RN-04",
            motivo_regra=(
                "Vasculhei a internet, mas não encontrei nenhum jornal ou veículo oficial noticiando isso "
                "ainda. Como não tenho dados sólidos, prefiro não tirar conclusões precipitadas."
            ),
            exibe_porcentagem=False,
        )

    # Confirmar exige corroboração de MAIS DE UMA fonte independente. Uma redação só
    # dizendo algo não é "corroboração" no sentido do produto — o valor está em várias
    # redações independentes baterem no mesmo fato. Sem esta guarda, o motor cravava
    # "provavelmente verdadeira" com base num único veículo (ex.: "Neymar namora a
    # Virginia" com uma fonte), e um modelo pequeno confirmando uma notícia solta vira
    # fake aprovada. Abaixo de dois apoios independentes, o teto é Inconclusiva — não
    # desmente, só se recusa a cravar. Não mexe em veredito de falsa: fake se sustenta
    # por contradição, não por corroboração.
    if (
        contexto.pipeline_encerrado
        and classificar(veracidade) in (Faixa.VERDADEIRA, Faixa.CONFIRMADA)
        and contexto.apoios_independentes < 2
    ):
        return Veredito(
            veracidade=veracidade,
            confianca=confianca,
            faixa=Faixa.INCONCLUSIVA,
            regra_aplicada="RN-04",
            motivo_regra=(
                "Achei só uma fonte dizendo isso. Uma redação sozinha não me basta "
                "para confirmar — eu preciso ver o mesmo fato em mais de um veículo "
                "independente. Por ora, fica em aberto: não dá para cravar."
            ),
            exibe_porcentagem=False,
        )

    return Veredito(
        veracidade=veracidade,
        confianca=confianca,
        faixa=classificar(veracidade),
    )
