import pytest
from src.core.entities.claim import NoticiaRequest
from src.core.engine.orchestrator import CamadaVerificacao, Orquestrador

class MockLayer(CamadaVerificacao):
    """Uma camada falsa para podermos testar a esteira do Orquestrador sem depender de IA."""
    def __init__(self, name, modify_c=0.0, modify_v=0.0):
        super().__init__()
        self.name = name
        self.modify_c = modify_c
        self.modify_v = modify_v

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        noticia.resultado.camada_atual = self.name
        noticia.resultado.confianca += self.modify_c
        noticia.resultado.veracidade += self.modify_v
        noticia.resultado.explicacao += f"[{self.name}] "
        return self.repassar(noticia)

def test_orquestrador_para_imediatamente_se_tem_certeza_absoluta():
    """
    US: Orquestração e Regra de Parada
    Dado que a Camada N0 tem certeza absoluta (ex: Cache V=100, C=1.0)
    Quando o Orquestrador repassar o fluxo,
    Então o pipeline deve parar na N0 e não rodar a N1.
    """
    n0 = MockLayer("N0", modify_c=1.0, modify_v=50.0) # V vai de 50 para 100, C vai para 1.0
    n1 = MockLayer("N1", modify_c=0.1, modify_v=-10.0)
    
    # Encadeia: N0 -> N1
    n0.set_proxima(n1)
    orquestrador = Orquestrador(n0)
    
    noticia = NoticiaRequest(texto="Notícia já verificada ontem.")
    resultado = orquestrador.checar(noticia)
    
    # Asserções
    assert resultado.resultado.camada_atual == "N0"
    assert "[N1]" not in resultado.resultado.explicacao, "A N1 não deveria ter sido executada!"
    assert resultado.resultado.confianca == 1.0

def test_orquestrador_continua_se_estiver_na_zona_de_duvida():
    """
    US: Orquestração e Regra de Parada
    Dado que a Camada tem alta confiança (C=0.9), mas V=50 (Zona de Dúvida),
    Então o sistema NÃO pode parar, deve repassar para a próxima camada.
    """
    n0 = MockLayer("N0", modify_c=0.9, modify_v=0.0) # V continua 50, C vai para 0.9 (DÚVIDA)
    n1 = MockLayer("N1", modify_c=0.0, modify_v=40.0) # N1 tira da dúvida (V vai para 90)
    n2 = MockLayer("N2") 
    
    # Encadeia: N0 -> N1 -> N2
    n0.set_proxima(n1).set_proxima(n2)
    orquestrador = Orquestrador(n0)
    
    noticia = NoticiaRequest(texto="Notícia com duplo sentido.")
    resultado = orquestrador.checar(noticia)
    
    # Asserções
    assert "[N0]" in resultado.resultado.explicacao
    assert "[N1]" in resultado.resultado.explicacao
    assert "[N2]" not in resultado.resultado.explicacao, "Deveria ter parado na N1, pois ela tirou da dúvida."
    assert resultado.resultado.camada_atual == "N1"

def test_orquestrador_percorre_todas_as_camadas_se_dificil():
    """
    US: Orquestração e Regra de Parada
    Dado que o texto é muito difícil e a confiança cresce pouco a pouco,
    Então o orquestrador deve percorrer toda a corrente até a N4 (LLM).
    """
    n0 = MockLayer("N0", modify_c=0.1)
    n1 = MockLayer("N1", modify_c=0.1)
    n2 = MockLayer("N2", modify_c=0.1)
    n3 = MockLayer("N3", modify_c=0.1)
    n4 = MockLayer("N4", modify_c=0.1)
    
    # Encadeia: N0 -> N1 -> N2 -> N3 -> N4
    n0.set_proxima(n1).set_proxima(n2).set_proxima(n3).set_proxima(n4)
    orquestrador = Orquestrador(n0)
    
    noticia = NoticiaRequest(texto="Notícia inédita, sarcástica e sem fontes.")
    resultado = orquestrador.checar(noticia)
    
    assert "[N0]" in resultado.resultado.explicacao
    assert "[N4]" in resultado.resultado.explicacao
    assert resultado.resultado.camada_atual == "N4"
    assert resultado.resultado.confianca == 0.5  # 5 * 0.1
