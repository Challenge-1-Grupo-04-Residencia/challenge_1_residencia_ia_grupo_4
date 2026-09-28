import pytest
from src.core.entities.claim import NoticiaRequest
from src.core.engine.n2_content import CamadaN2Conteudo

@pytest.fixture
def camada_n2():
    """Fixture que instancializa a Camada N2 antes de cada teste."""
    return CamadaN2Conteudo()

def test_texto_curto_ignorado_n2(camada_n2):
    """Garante que frases menores que 10 palavras são ignoradas pela ML."""
    # Texto com menos de 10 palavras
    noticia = NoticiaRequest(texto="O ministro pediu demissão nesta manhã.")
    
    # Processa na N2
    resultado = camada_n2.processar(noticia)
    
    # A veracidade não deve ter mudado da base (50.0) e a explicação deve constar o salto
    assert resultado.resultado.veracidade == 50.0
    assert "Texto muito curto" in resultado.resultado.explicacao

def test_texto_sensacionalista_punido(camada_n2):
    """Garante que uma frase com estilo manipulativo sofra punição de veracidade."""
    noticia = NoticiaRequest(texto="URGENTE!!! REPASSEM PARA TODOS!!! O governo quer matar a população com as novas vacinas que contêm chip!!! Acordem povo brasileiro!!! Cuidado!!!")
    resultado = camada_n2.processar(noticia)
    
    # Só roda as asserções de ML se o arquivo .joblib estiver presente no disco
    if camada_n2.modelo is not None:
        assert resultado.resultado.veracidade < 50.0, "A veracidade deveria ter caído"
        assert resultado.resultado.confianca > 0.0, "O sistema deveria ter ganho confiança"
        assert "estilo de escrita apelativo" in resultado.resultado.explicacao
    else:
        pytest.skip("Modelo de ML (.joblib) não carregado.")

def test_texto_jornalistico_aprovado(camada_n2):
    """Garante que textos limpos e sóbrios passem ilesos."""
    noticia = NoticiaRequest(texto="Nesta terça-feira, o Ministério da Saúde anunciou uma nova campanha de vacinação nacional contra o vírus da gripe. A medida visa proteger a população.")
    resultado = camada_n2.processar(noticia)
    
    if camada_n2.modelo is not None:
        # A explicação deve ser neutra para textos limpos
        assert "não aparenta ser sensacionalista" in resultado.resultado.explicacao
    else:
        pytest.skip("Modelo de ML (.joblib) não carregado.")
