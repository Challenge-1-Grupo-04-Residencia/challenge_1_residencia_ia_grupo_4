"""Testes do motor de veracidade e confiança (RF-09, issue #20)."""

import pytest

from src.core.engine import scoring
from src.core.engine.scoring import Faixa
from src.core.entities.signal import PESO_TOTAL, medir


def test_peso_total_do_catalogo_fecha_em_cem():
    """As três dimensões somam 35 + 25 + 40. Se não fecharem, a cobertura mente."""
    assert PESO_TOTAL == 100


def test_sinal_sem_dado_nao_conta_como_zero():
    """RN-06: um sinal indisponível sai do cálculo, não derruba o score."""
    so_disponivel = [medir("S-01", 1.0)]
    com_indisponivel = [medir("S-01", 1.0), medir("S-06", None)]

    assert scoring.calcular_veracidade(so_disponivel) == 100.0
    assert scoring.calcular_veracidade(com_indisponivel) == 100.0


def test_sinal_indisponivel_reduz_a_confianca_mas_nao_o_score():
    """Não saber é diferente de saber que é ruim: afeta a confiança, não a veracidade."""
    parcial = [medir("S-01", 1.0)]
    completo = [medir("S-01", 1.0), medir("S-11", 1.0)]

    assert scoring.calcular_veracidade(parcial) == scoring.calcular_veracidade(completo)
    assert scoring.calcular_confianca(parcial) < scoring.calcular_confianca(completo)


def test_veracidade_e_none_sem_nenhum_sinal():
    """Sem evidência não há score. Devolver 50 faria 'não sei' virar 'está na dúvida'."""
    assert scoring.calcular_veracidade([]) is None
    assert scoring.calcular_veracidade([medir("S-01", None)]) is None


def test_media_ponderada_respeita_os_pesos():
    """S-01 pesa 12 e S-05 pesa 4: o sinal pesado domina a média."""
    sinais = [medir("S-01", 1.0), medir("S-05", 0.0)]
    # (12*1 + 4*0) / (12+4) = 0,75
    assert scoring.calcular_veracidade(sinais) == pytest.approx(75.0)


def test_exemplo_da_documentacao():
    """Reproduz o exemplo de ``docs/produto/classificacao.md``: V ≈ 12, cobertura 35%.

    Serve de âncora: se alguém mexer nos pesos sem atualizar a documentação, este
    teste quebra e obriga a registrar a mudança no histórico de calibração.

    Os 35% do exemplo são cobertura **do catálogo**, que é a conta que a documentação
    descreve. A ``cobertura`` que alimenta a confiança passou a ser relativa ao que as
    camadas existentes sabem medir — ver :func:`scoring.cobertura`.
    """
    sinais = [
        medir("S-03", 0.0),   # domínio com 20 dias
        medir("S-04", 0.25),  # sem autor, sem expediente
        medir("S-05", 0.0),   # autor anônimo
        medir("S-06", 0.15),  # classificador
        medir("S-07", 0.1),   # muito sensacionalista
        medir("S-08", 0.2),   # pico de medo
    ]
    veracidade = scoring.calcular_veracidade(sinais)

    assert veracidade == pytest.approx(12.14, abs=0.1)
    assert scoring.cobertura_do_catalogo(sinais) == pytest.approx(0.35)
    assert scoring.classificar(veracidade) is Faixa.FALSA


def test_confianca_cresce_com_a_cobertura():
    """Mais peso observado, mais confiança — mantida a concordância."""
    pouco = [medir("S-05", 1.0)]
    muito = [medir("S-01", 1.0), medir("S-02", 1.0), medir("S-03", 1.0)]

    assert scoring.calcular_confianca(pouco) < scoring.calcular_confianca(muito)


def test_dimensoes_discordantes_derrubam_a_confianca():
    """Fonte ótima e conteúdo péssimo é sinal de que algo não fecha."""
    concordam = [medir("S-01", 1.0), medir("S-06", 1.0)]
    discordam = [medir("S-01", 1.0), medir("S-06", 0.0)]

    assert scoring.calcular_confianca(discordam) < scoring.calcular_confianca(concordam)


def test_confianca_fica_no_intervalo_valido():
    """Nenhuma combinação de sinais pode produzir confiança fora de [0, 1]."""
    for score in (0.0, 0.5, 1.0):
        sinais = [medir(sid, score) for sid in ("S-01", "S-06", "S-11")]
        assert 0.0 <= scoring.calcular_confianca(sinais) <= 1.0


def test_uma_dimensao_sozinha_nao_infla_a_confianca():
    """Com uma só dimensão a concordância é 1, mas a cobertura segura o resultado."""
    sinais = [medir("S-01", 1.0), medir("S-02", 1.0)]  # só dimensão Fonte, peso 20

    assert scoring.concordancia(sinais) == 1.0
    assert scoring.calcular_confianca(sinais) < scoring.C_MIN


def test_cobertura_nao_desconta_camada_que_nao_existe():
    """Medir tudo o que as camadas implementadas sabem medir dá cobertura cheia.

    Antes o denominador eram os 100 pontos do catálogo, então o teto da confiança era
    0,63 enquanto N0 e N1 não existissem — e a regra de parada de RN-07, que exige
    C ≥ 0,6, era inalcançável. A lacuna do catálogo continua visível em
    :func:`scoring.cobertura_do_catalogo`.
    """
    tudo_que_sabemos_medir = [
        medir(sid, 1.0)
        for sid in ("S-06", "S-07", "S-08", "S-09", "S-11", "S-12", "S-13")
    ]

    assert scoring.cobertura(tudo_que_sabemos_medir) == pytest.approx(1.0)
    assert scoring.cobertura_do_catalogo(tudo_que_sabemos_medir) == pytest.approx(0.63)


def test_cobertura_nunca_passa_de_um_com_sinal_de_camada_futura():
    """Quando N1 começar a emitir sinal, a conta tem de continuar fechando em 1."""
    sinais = [
        medir(sid, 1.0)
        for sid in ("S-01", "S-02", "S-03", "S-04", "S-05",
                    "S-06", "S-07", "S-08", "S-09", "S-11", "S-12", "S-13")
    ]

    assert scoring.cobertura(sinais) == pytest.approx(1.0)


def test_dimensoes_em_discordancia_total_derrubam_a_concordancia_pela_metade():
    """Conteúdo ótimo e corroboração péssima é o pior caso: σ = 0,5.

    A fórmula é ``1 - σ`` e o desvio populacional de dois valores em [0, 1] não passa
    de 0,5, então o piso da concordância com duas dimensões é 0,5. Amplificar isso foi
    tentado e desfeito — ver :func:`scoring.concordancia`.
    """
    sinais = [medir("S-06", 1.0), medir("S-11", 0.0)]

    assert scoring.concordancia(sinais) == pytest.approx(0.5)
    assert scoring.concordancia(sinais) < scoring.concordancia(
        [medir("S-06", 1.0), medir("S-11", 1.0)]
    )


def test_regra_de_parada_e_alcancavel_ao_fim_da_n3():
    """RN-07: sem isto a LLM da N4 roda em 100% das checagens e o produto não fecha.

    Estilo claramente falso e nenhuma corroboração encontrada é caso resolvido na N3 —
    não há pergunta que a LLM responda aqui que justifique o custo.
    """
    ate_a_n3 = [
        medir("S-06", 0.05),
        medir("S-07", 0.1),
        medir("S-08", 0.1),
        medir("S-09", 0.0),
        medir("S-11", 0.0),
        medir("S-13", 0.1),
    ]
    veracidade = scoring.calcular_veracidade(ate_a_n3)
    confianca = scoring.calcular_confianca(ate_a_n3)

    assert scoring.deve_parar(veracidade, confianca)


@pytest.mark.parametrize(
    ("veracidade", "faixa"),
    [
        (0, Faixa.FALSA),
        (20, Faixa.FALSA),
        (21, Faixa.DUVIDOSA),
        (40, Faixa.DUVIDOSA),
        (41, Faixa.INCONCLUSIVA),
        (60, Faixa.INCONCLUSIVA),
        (61, Faixa.VERDADEIRA),
        (80, Faixa.VERDADEIRA),
        (81, Faixa.CONFIRMADA),
        (100, Faixa.CONFIRMADA),
    ],
)
def test_faixas_de_veracidade(veracidade, faixa):
    """Os limites das faixas batem com a tabela da documentação."""
    assert scoring.classificar(veracidade) is faixa


class TestRegraDeParada:
    """RF-08 — quando a Vera pode parar de subir camadas."""

    def test_para_com_confianca_alta_e_score_baixo(self):
        assert scoring.deve_parar(veracidade=10.0, confianca=0.8)

    def test_para_com_confianca_alta_e_score_alto(self):
        assert scoring.deve_parar(veracidade=90.0, confianca=0.8)

    def test_nao_para_na_zona_de_duvida_mesmo_com_confianca_alta(self):
        """Resultado ambíguo com confiança alta ainda não responde ao usuário."""
        assert not scoring.deve_parar(veracidade=50.0, confianca=0.95)

    def test_nao_para_com_confianca_baixa_mesmo_com_score_extremo(self):
        assert not scoring.deve_parar(veracidade=5.0, confianca=0.3)

    def test_nao_para_sem_score(self):
        assert not scoring.deve_parar(veracidade=None, confianca=1.0)


def test_principais_sinais_ordena_por_contribuicao():
    """RN-05 pede os principais sinais: peso alto com score extremo explica mais."""
    sinais = [
        medir("S-05", 0.0),   # peso 4, extremo  -> 4 * 0,5 = 2,0
        medir("S-12", 0.5),   # peso 20, neutro  -> 20 * 0,0 = 0,0
        medir("S-01", 0.0),   # peso 12, extremo -> 12 * 0,5 = 6,0
    ]
    principais = scoring.principais_sinais(sinais, limite=2)

    assert [s.id for s in principais] == ["S-01", "S-05"]


def test_principais_sinais_ignora_indisponiveis():
    sinais = [medir("S-12", None), medir("S-05", 0.0)]
    assert [s.id for s in scoring.principais_sinais(sinais)] == ["S-05"]
