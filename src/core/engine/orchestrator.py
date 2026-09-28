from abc import ABC, abstractmethod
from typing import Optional
from src.core.entities.claim import NoticiaRequest

class CamadaVerificacao(ABC):
    """
    Interface base para o padrão Chain of Responsibility.
    Cada Camada (N0, N1, N2, N3, N4) deve implementar esta interface.
    """
    def __init__(self):
        self.proxima_camada: Optional["CamadaVerificacao"] = None
        self.C_MIN = 0.7  # Limiar de confiança base

    def set_proxima(self, camada: "CamadaVerificacao") -> "CamadaVerificacao":
        self.proxima_camada = camada
        return camada

    @abstractmethod
    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        pass

    def atingiu_regra_parada(self, noticia: NoticiaRequest) -> bool:
        """
        Regra de parada conforme documentação:
        Para se C >= C_min E V estiver fora da zona de dúvida (V <= 25 ou V >= 75)
        """
        v = noticia.resultado.veracidade
        c = noticia.resultado.confianca
        
        if c >= self.C_MIN and (v <= 25.0 or v >= 75.0):
            return True
        return False

    def repassar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        if self.proxima_camada and not self.atingiu_regra_parada(noticia):
            return self.proxima_camada.processar(noticia)
        return noticia

class Orquestrador:
    """
    Constrói a corrente (Chain) e dispara a execução.
    """
    def __init__(self, camada_inicial: CamadaVerificacao):
        self.camada_inicial = camada_inicial

    def checar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        return self.camada_inicial.processar(noticia)
