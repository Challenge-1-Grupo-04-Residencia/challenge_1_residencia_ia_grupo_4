from unittest.mock import patch
from src.core.engine.n1_fonte import CamadaN1Fonte
from src.core.entities.claim import NoticiaRequest

# 1. Teste para Domínio Muito Novo (< 1 mês) -> Score 0.0
@patch("src.core.engine.n1_fonte.consultar_idade_meses")
def test_s03_penaliza_dominio_muito_recente(mock_whois):
    mock_whois.return_value = 0 # Domínio com 0 meses
    camada = CamadaN1Fonte()
    noticia = NoticiaRequest(texto="Veja isso!", url="https://siterecente.com/noticia")
    
    resposta = camada.processar(noticia)
    s03 = next((s for s in resposta.resultado.sinais if s.id == "S-03"), None)
    
    assert s03 is not None
    assert s03.score == 0.0
    assert "muito recente" in s03.justificativa

# 2. Teste para Domínio Relativamente Novo (1 a 6 meses) -> Score 0.3
@patch("src.core.engine.n1_fonte.consultar_idade_meses")
def test_s03_penaliza_dominio_relativamente_novo(mock_whois):
    mock_whois.return_value = 3 # Domínio com 3 meses
    camada = CamadaN1Fonte()
    noticia = NoticiaRequest(texto="Veja isso!", url="https://sitenovo.com/noticia")
    
    resposta = camada.processar(noticia)
    s03 = next((s for s in resposta.resultado.sinais if s.id == "S-03"), None)
    
    assert s03 is not None
    assert s03.score == 0.3

# 3. Teste para Domínio Estabelecido (6 a 24 meses) -> Score 0.6
@patch("src.core.engine.n1_fonte.consultar_idade_meses")
def test_s03_dominio_estabelecido(mock_whois):
    mock_whois.return_value = 12 # Domínio com 1 ano
    camada = CamadaN1Fonte()
    noticia = NoticiaRequest(texto="Veja isso!", url="https://siteok.com/noticia")
    
    resposta = camada.processar(noticia)
    s03 = next((s for s in resposta.resultado.sinais if s.id == "S-03"), None)
    
    assert s03 is not None
    assert s03.score == 0.6

# 4. Teste para Domínio Antigo (> 24 meses) -> Score 1.0
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