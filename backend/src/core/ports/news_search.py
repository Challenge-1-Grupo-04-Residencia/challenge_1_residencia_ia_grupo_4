"""Porta de busca de notícias semelhantes (RF-27).

O núcleo depende desta interface, nunca de GDELT, RSS ou de um índice TF-IDF concreto.
Assim a camada N3 pode ser testada com um buscador falso, e trocar a fonte de notícias
não toca no motor de veracidade.
"""

from typing import Protocol

from src.core.entities.claim import DocumentoRelacionado


class BuscaIndisponivel(Exception):
    """A busca não pôde ser feita: rede fora, provedor fora, limite de uso estourado.

    Existe para separar duas coisas que antes chegavam na N3 como a mesma lista vazia:
    *ninguém publicou nada sobre isso* e *eu não consegui procurar*. Nenhuma das duas
    vira evidência de falsidade — por RN-06 as duas deixam o sinal indisponível —, mas o
    que a Vera diz ao usuário muda, e a equipe precisa saber quando a camada está no
    chão em vez de descobrir pelo silêncio.
    """


class BuscadorDeNoticias(Protocol):
    """Encontra notícias publicadas que falam do mesmo fato que o texto consultado."""

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        """Devolve até ``top_k`` documentos, do mais ao menos semelhante.

        Lista vazia significa que a busca funcionou e não achou nada. Indisponibilidade
        levanta :class:`BuscaIndisponivel`, que a camada N3 traduz em sinal indisponível
        com justificativa própria.
        """
        ...
