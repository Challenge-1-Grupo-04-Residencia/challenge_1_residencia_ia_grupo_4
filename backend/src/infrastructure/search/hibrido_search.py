from src.core.ports.news_search import BuscadorDeNoticias
from src.core.entities.claim import DocumentoRelacionado

class BuscadorHibrido(BuscadorDeNoticias):
    """
    Busca nas várias fontes que a Vera conhece (GDELT na web, e Vetorial no nosso banco)
    e junta os melhores resultados.
    """
    
    def __init__(self, buscadores: list[BuscadorDeNoticias]):
        self.buscadores = buscadores

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        todos_resultados = []
        
        for buscador in self.buscadores:
            resultados = buscador.buscar(texto, top_k=top_k)
            todos_resultados.extend(resultados)
            
        # Ordena os resultados pelas coisas mais parecidas que achamos (maior similaridade primeiro)
        todos_resultados.sort(key=lambda x: x.similaridade, reverse=True)
        
        # Pega só o Top K total para não explodir o limite de leitura da Llama 3
        return todos_resultados[:top_k]
