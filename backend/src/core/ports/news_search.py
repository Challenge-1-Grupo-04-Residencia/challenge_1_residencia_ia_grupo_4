"""Porta de busca de notícias semelhantes (RF-27).

O núcleo depende desta interface, nunca de GDELT, RSS ou de um índice TF-IDF concreto.
Assim a camada N3 pode ser testada com um buscador falso, e trocar a fonte de notícias
não toca no motor de veracidade.
"""

from typing import Protocol

from src.core.entities.claim import DocumentoRelacionado


class BuscadorDeNoticias(Protocol):
    """Encontra notícias publicadas que falam do mesmo fato que o texto consultado."""

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        """Devolve até ``top_k`` documentos, do mais ao menos semelhante.

        Implementações não devem levantar exceção por indisponibilidade de rede: uma
        busca que falha devolve lista vazia, e a camada N3 traduz isso em sinal
        indisponível (RN-06) em vez de em evidência de falsidade.
        """
        ...
