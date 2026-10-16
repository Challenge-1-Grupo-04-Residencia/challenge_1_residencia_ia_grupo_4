"""Testes do sinal de intensidade emocional manipulativa (RF-23, S-08).

O léxico deste módulo foi calibrado contra 15.854 textos rotulados dos corpora do
projeto, e os números citados nos testes vêm dessa medição.
"""

from src.core.engine import emotion


def test_texto_sem_vocabulario_emocional_fica_sem_medida():
    """Nada para medir é ``None``, não zero — RN-06.

    Um zero aqui virava score 1,0 na camada e somava veracidade a qualquer texto
    educado, inclusive a uma saudação.
    """
    indice, emocao = emotion.indice_intensidade_emocional(
        "O tempo hoje está nublado com chances de chuva."
    )

    assert indice is None
    assert emocao == ""


def test_texto_vazio_nao_quebra():
    assert emotion.indice_intensidade_emocional("") == (None, "")


def test_detecta_degradacao_moral_e_ignora_maiusculas():
    texto = "Esses BANDIDOS são uns VAGABUNDOS, ladrões canalhas e vermes podres!"
    indice, emocao = emotion.indice_intensidade_emocional(texto)

    assert indice == 1.0
    assert emocao == "raiva"


def test_noticia_triste_nao_e_manipulacao_emocional():
    """"morte", "crise", "risco" e "doença" aparecem mais em notícia verdadeira.

    Medidas nos corpora: lift 0,50, 0,27, 0,29 e 0,27 respectivamente — isto é, de duas
    a quatro vezes mais frequentes em texto **verdadeiro**. Enquanto estavam no léxico,
    S-08 tinha AUC 0,39, abaixo do acaso e apontando para o lado errado.
    """
    texto = (
        "O Ministério da Saúde confirmou a morte de um paciente por dengue. Segundo a "
        "Fiocruz, o risco de novos casos segue alto durante a crise sazonal da doença, "
        "que exige cuidado redobrado e atenção ao perigo de novas infecções."
    )

    assert emotion.indice_intensidade_emocional(texto)[0] is None


def test_uma_palavra_em_texto_longo_nao_satura():
    """Antes, uma só palavra do léxico em 33 já saturava o índice em 100%.

    O efeito era que toda justificativa dizia "carga emocional intensa (100%)" e não
    informava nada ao usuário.
    """
    texto = (
        "O relatório do instituto aponta que o número de ocorrências registradas pela "
        "polícia caiu no trimestre encerrado em agosto, na comparação com o mesmo "
        "período do ano anterior. Um bandido foi preso durante a operação, segundo a "
        "corporação, que divulgou o balanço nesta semana em sua página oficial e "
        "detalhou a metodologia usada na apuração dos dados consolidados do período, "
        "além de apresentar a série histórica completa desde o início da coleta."
    )
    indice, emocao = emotion.indice_intensidade_emocional(texto)

    assert indice is not None
    assert 0.0 < indice < 1.0
    assert emocao == "raiva"


def test_densidade_maior_da_indice_maior():
    pouco = emotion.indice_intensidade_emocional(
        "O relatório do instituto aponta que o número de ocorrências registradas pela "
        "polícia caiu no trimestre encerrado em agosto, na comparação com o mesmo "
        "período do ano anterior. Um bandido foi preso durante a operação, segundo a "
        "corporação, que divulgou o balanço nesta semana em sua página oficial e "
        "detalhou a metodologia usada na apuração dos dados consolidados do período, "
        "além de apresentar a série histórica completa desde o início da coleta."
    )[0]
    muito = emotion.indice_intensidade_emocional(
        "Bandidos vagabundos, ladrões canalhas, vermes podres e corruptos nojentos."
    )[0]

    assert pouco < muito


def test_lexico_nao_contem_termo_de_identidade_politica():
    """RN-08: viés político é contexto e não altera o score.

    A mineração por *lift* nos corpora traz "comunista" (3,6) e "esquerdista" (7,7) no
    topo. Incluí-los melhoraria a métrica e violaria a regra — a Vera passaria a
    descontar veracidade de quem usa certo vocabulário político.
    """
    proibidos = {
        "comunista", "comunistas", "comunismo", "socialista", "socialistas",
        "esquerdista", "esquerdistas", "direitista", "petista", "bolsonarista",
        "fascista", "ditador", "messias",
    }

    assert not proibidos & set(emotion.LEXICO_EMOCIONAL_PT)
