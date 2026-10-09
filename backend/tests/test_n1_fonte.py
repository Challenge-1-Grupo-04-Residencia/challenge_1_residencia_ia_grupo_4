from unittest.mock import patch
from src.core.engine.n1_fonte import CamadaN1Fonte
from src.core.entities.claim import NoticiaRequest

# 1. Teste para Domínio Novo (Penaliza score para 0.0)
@patch("src.core.engine.n1_fonte.consultar_idade_meses")
def test_s03_penaliza_dominio_recente(mock_whois):
    mock_whois.return_value = 2 # Domínio com 2 meses
    camada = CamadaN1Fonte()
    noticia = NoticiaRequest(texto="Veja isso!", url="https://siterecente.com/noticia")
    
    resposta = camada.processar(noticia)
    
    # Busca o sinal S-03 nos resultados
    s03 = next((s for s in resposta.resultado.sinais if s.id == "S-03"), None)
    
    assert s03 is not None
    assert s03.score == 0.0
    assert "muito recente" in s03.justificativa

# 2. Teste para Domínio Antigo (Aprova score para 1.0)
@patch("src.core.engine.n1_fonte.consultar_idade_meses")
def test_s03_aprova_dominio_antigo(mock_whois):
    mock_whois.return_value = 120 # Domínio com 10 anos
    camada = CamadaN1Fonte()
    noticia = NoticiaRequest(texto="Notícia real", url="https://siteantigo.com/noticia")
    
    resposta = camada.processar(noticia)
    s03 = next((s for s in resposta.resultado.sinais if s.id == "S-03"), None)
    
    assert s03 is not None
    assert s03.score == 1.0

# 3. Teste para Falha da API (Deve registrar como nao_medido)
@patch("src.core.engine.n1_fonte.consultar_idade_meses")
def test_s03_quando_api_falha(mock_whois):
    mock_whois.return_value = None # Simula queda da API ou falta de chave
    camada = CamadaN1Fonte()
    noticia = NoticiaRequest(texto="Teste API", url="https://sitequalquer.com/noticia")
    
    resposta = camada.processar(noticia)
    s03 = next((s for s in resposta.resultado.sinais if s.id == "S-03"), None)
    
    assert s03 is not None
    assert s03.score is None # Score None e aferido=False (não medido)
    assert s03.aferido is False