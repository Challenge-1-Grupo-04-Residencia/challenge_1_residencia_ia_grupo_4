from backend.src.core.engine import emotion

def test_texto_sem_emocoes_manipulativas_retorna_zero():
    texto = "O tempo hoje está nublado com chances de chuva."
    indice, emocao = emotion.indice_intensidade_emocional(texto)
    assert indice == 0.0
    assert emocao == ""

def test_detecta_densidade_de_raiva_e_ignora_maiusculas():
    texto = "Isso é um ABSURDO! Um ROUBO contra a nação! Que VERGONHA desses canalhas!!!"
    indice, emocao = emotion.indice_intensidade_emocional(texto)
    assert indice == 1.0  # Satura em 100%
    assert emocao == "raiva"

def test_detecta_densidade_de_medo_com_pontuacao_grudada():
    texto = "Atenção: o vírus, fatal, causará uma crise e destruição. Risco de morte!"
    indice, emocao = emotion.indice_intensidade_emocional(texto)
    assert indice == 1.0  # Satura
    assert emocao == "medo"

def test_calculo_parcial_nao_satura():
    texto = "O IBGE publicou um estudo longo. Infelizmente os dados da crise foram piores do que o esperado."
    indice, emocao = emotion.indice_intensidade_emocional(texto)
    # Tem "crise" (medo), mas num texto razoavelmente grande.
    assert 0.0 < indice < 1.0
    assert emocao == "medo"
