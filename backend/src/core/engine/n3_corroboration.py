"""Camada N3 · Corroboração — verifica se **outros** publicaram o mesmo fato.

Responde à pergunta que mais pesa no score: uma notícia relevante que nenhum veículo
sério replicou é suspeita, e uma que saiu em três redações independentes dificilmente
é fabricação. A dimensão Corroboração vale 40 dos 100 pontos, e 15 deles são S-11,
medido aqui (RF-27, RF-28).

A camada recebe um :class:`BuscadorDeNoticias` por injeção, então funciona igual com
GDELT, com índice TF-IDF local ou com um buscador falso em teste.
"""

from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import DocumentoRelacionado, NoticiaRequest
from src.core.entities.signal import medir
from src.core.ports.news_search import BuscadorDeNoticias

#: S-11 pela contagem de veículos confiáveis distintos, conforme a tabela de sinais:
#: 0 → 0 · 1 → 0,5 · 2 → 0,8 · 3+ → 1.
_SCORE_POR_CONTAGEM: dict[int, float] = {0: 0.0, 1: 0.5, 2: 0.8}

#: Acima desta similaridade dois textos são praticamente o mesmo conteúdo. Se o veículo
#: de origem não for confiável, isso indica cópia — entrada de S-13 (RF-31).
LIMIAR_DE_COPIA = 0.9


class CamadaN3Corroboracao(CamadaVerificacao):
    """Busca notícias semelhantes e mede a corroboração por veículos confiáveis."""

    def __init__(self, buscador: BuscadorDeNoticias, top_k: int = 5):
        super().__init__()
        self.buscador = buscador
        #: A US pede o top-5 de documentos relacionados.
        self.top_k = top_k

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        resultado = noticia.resultado
        resultado.camada_atual = "N3"

        relacionados = self.buscador.buscar(noticia.texto, top_k=self.top_k)
        resultado.documentos_relacionados = relacionados

        if not relacionados:
            # Pode ser "ninguém publicou" ou "a busca falhou" — são coisas diferentes e
            # não dá para distingui-las aqui, então o sinal fica indisponível em vez de
            # virar evidência de falsidade.
            resultado.registrar(
                medir(
                    "S-11",
                    None,
                    "A busca por notícias semelhantes não devolveu resultados.",
                )
            )
            resultado.explicacao += " Não encontrei outras publicações sobre o assunto."
            return self.repassar(noticia)

        self._medir_corroboracao(relacionados, resultado)
        self._medir_originalidade(relacionados, resultado)
        resultado.fontes_citadas.extend(d.url for d in relacionados if d.url)
        # A N4 compara cada evidência com a alegação do texto; é a N3 que as recolhe.
        resultado.evidencias.extend(d.titulo for d in relacionados if d.titulo)

        return self.repassar(noticia)

    def _medir_corroboracao(
        self, relacionados: list[DocumentoRelacionado], resultado
    ) -> None:
        """S-11 — quantos veículos confiáveis **distintos** publicaram o mesmo fato.

        A contagem é por domínio, não por artigo: cinco matérias do mesmo portal são
        uma corroboração, não cinco.
        """
        confiaveis = {d.fonte for d in relacionados if d.fonte_confiavel and d.fonte}
        quantidade = len(confiaveis)
        score = _SCORE_POR_CONTAGEM.get(quantidade, 1.0)

        if quantidade == 0:
            justificativa = (
                "Encontrei publicações semelhantes, mas nenhuma em veículo da base "
                "curada."
            )
        else:
            nomes = ", ".join(sorted(confiaveis))
            plural = "veículos confiáveis publicaram" if quantidade > 1 else "veículo confiável publicou"
            justificativa = f"{quantidade} {plural} o mesmo fato: {nomes}."

        resultado.registrar(medir("S-11", score, justificativa))
        resultado.explicacao += f" {justificativa}"

    def _medir_originalidade(
        self, relacionados: list[DocumentoRelacionado], resultado
    ) -> None:
        """S-13 — o texto é cópia quase literal de uma fonte não confiável?

        Similaridade altíssima com veículo confiável é replicação legítima de conteúdo
        de agência, e não penaliza. O sinal só aponta falsidade quando a quase-cópia
        vem de fora da base curada.
        """
        quase_copias = [d for d in relacionados if d.similaridade >= LIMIAR_DE_COPIA]
        if not quase_copias:
            resultado.registrar(
                medir("S-13", 1.0, "Não parece cópia de outra publicação.")
            )
            return

        if any(d.fonte_confiavel for d in quase_copias):
            resultado.registrar(
                medir(
                    "S-13",
                    1.0,
                    "O texto replica fielmente uma publicação de veículo confiável.",
                )
            )
            return

        resultado.registrar(
            medir(
                "S-13",
                0.0,
                "O texto é quase idêntico a uma publicação de fonte não confiável.",
            )
        )
