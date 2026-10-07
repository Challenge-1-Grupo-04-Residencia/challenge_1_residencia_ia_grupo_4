from unittest.mock import patch, MagicMock
from src.core.entities.claim import NoticiaRequest
from src.core.engine.n0_cache import CamadaN0Cache

def test_n0_cache_hit_retorna_falso():
    """Se o banco de dados tiver um desmentido como 'Falso', a N0 deve parar o fluxo e aplicar nota 0.0."""
    # 1. Preparação
    noticia = NoticiaRequest(texto="Qualquer texto", url="https://fake.com")
    camada_n0 = CamadaN0Cache()
    
    # Criamos um "dublê" do banco de dados (para os testes rodarem ultra rápido sem precisar do Postgres)
    mock_hit = MagicMock()
    mock_hit.veredicto = "Falso"
    mock_hit.agencia = "Lupa"
    
    with patch("src.core.engine.n0_cache.SessionLocal") as mock_session:
        # Simulamos que o banco encontrou a notícia!
        mock_db = mock_session.return_value.__enter__.return_value
        mock_db.query.return_value.filter.return_value.first.return_value = mock_hit
        
        # 2. Execução
        resultado = camada_n0.processar(noticia)
        
        # 3. Verificação
        assert resultado.resultado.camada_atual == "N0"
        assert len(resultado.resultado.sinais) == 1
        
        sinal = resultado.resultado.sinais[0]
        assert sinal.id == "S-00"
        assert sinal.score == 0.0  # Confirma que a nota foi 0 (Falso)
        assert "Lupa" in sinal.justificativa

def test_n0_cache_miss_repassa_adiante():
    """Se a notícia NÃO existir no banco, a N0 deve repassar silenciosamente para a próxima camada."""
    noticia = NoticiaRequest(texto="Link novo", url="https://site.com")
    
    camada_n0 = CamadaN0Cache()
    # Criamos uma próxima camada imaginária (N2)
    proxima_camada = MagicMock()
    camada_n0.set_proxima(proxima_camada)
    
    with patch("src.core.engine.n0_cache.SessionLocal") as mock_session:
        # Simulamos que o banco buscou e retornou NADA (None)
        mock_db = mock_session.return_value.__enter__.return_value
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        camada_n0.processar(noticia)
        
        # Garante que ele chamou a próxima camada já que não achou no cache!
        proxima_camada.processar.assert_called_once_with(noticia)
