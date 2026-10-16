import logging

from src.core.ports.news_search import BuscadorDeNoticias, BuscaIndisponivel
from src.core.entities.claim import DocumentoRelacionado

_log = logging.getLogger(__name__)


class BuscadorHibrido(BuscadorDeNoticias):
    """
    Busca nas várias fontes que a Vera conhece (Google Notícias na web e o banco
    Vetorial local) e junta os melhores resultados.

    Uma fonte fora do ar **não** derruba as demais (RN-06): o híbrido só fica
    indisponível quando *todas* as fontes ficam. Antes, a primeira fonte a falhar
    (ex.: Google Notícias em timeout) levantava ``BuscaIndisponivel`` e matava a busca
    inteira — a N3 dizia "não consegui procurar" mesmo com o banco vetorial de pé, e o
    que ele tinha a dizer era descartado.
    """

    def __init__(self, buscadores: list[BuscadorDeNoticias]):
        self.buscadores = buscadores

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        todos_resultados: list[DocumentoRelacionado] = []
        indisponiveis = 0

        for buscador in self.buscadores:
            try:
                resultados = buscador.buscar(texto, top_k=top_k)
            except BuscaIndisponivel as erro:
                # Falha de uma fonte é limitação daquela fonte, não evidência sobre a
                # notícia. Registra e segue para as outras.
                indisponiveis += 1
                _log.warning(
                    "Fonte %s indisponível: %s", type(buscador).__name__, erro
                )
                continue
            todos_resultados.extend(resultados)

        # Só propaga indisponibilidade se nenhuma fonte conseguiu procurar. Com ao menos
        # uma fonte de pé, lista vazia significa "procurei e não achei" — que é diferente
        # de "não consegui procurar", e a N3 fala as duas coisas de formas diferentes.
        if self.buscadores and indisponiveis == len(self.buscadores):
            raise BuscaIndisponivel(
                "Nenhuma fonte de busca respondeu: todas estão indisponíveis."
            )

        # Ordena pelos mais parecidos primeiro.
        todos_resultados.sort(key=lambda x: x.similaridade, reverse=True)

        # Top K total para não estourar o limite de leitura da Llama 3.
        return todos_resultados[:top_k]
