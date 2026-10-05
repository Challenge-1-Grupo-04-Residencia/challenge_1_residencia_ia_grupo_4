"""Camada N3 · Corroboração — verifica se **outros** publicaram o mesmo fato.

Responde à pergunta que mais pesa no score: uma notícia relevante que nenhum veículo
sério replicou é suspeita, e uma que saiu em três redações independentes dificilmente
é fabricação. A dimensão Corroboração vale 40 dos 100 pontos, e 15 deles são S-11,
medido aqui (RF-27, RF-28).

A camada recebe um :class:`BuscadorDeNoticias` por injeção, então funciona igual com
GDELT, com índice TF-IDF local ou com um buscador falso em teste.
"""

import logging

from src.core.engine import checagens_publicadas
from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import AnaliseResultado, DocumentoRelacionado, NoticiaRequest
from src.core.entities.signal import medir, nao_medido, sem_achado
from src.core.ports.news_search import BuscadorDeNoticias, BuscaIndisponivel

_log = logging.getLogger(__name__)

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

        try:
            relacionados = self.buscador.buscar(noticia.texto, top_k=self.top_k)
        except BuscaIndisponivel as erro:
            # Falha nossa não é evidência contra a notícia (RN-06). O detalhe técnico
            # vai para o log: antes a camada morria em silêncio e ninguém percebia.
            _log.warning("N3 sem corroboração: %s", erro)
            resultado.registrar(
                nao_medido(
                    "S-11",
                    "Não consegui consultar a base de notícias agora: a busca não "
                    "respondeu.",
                )
            )
            resultado.explicacao += (
                " Não consegui procurar outras publicações sobre o assunto agora — "
                "isso é limitação minha, não achado sobre a notícia."
            )
            return self.repassar(noticia)

        resultado.documentos_relacionados = relacionados

        if not relacionados:
            # A busca rodou. Não achar publicação é informação, mas não é a mesma
            # coisa que "nenhum veículo confiável publicou": a cobertura do buscador é
            # enviesada para notícia recente, e dar 0,0 aqui penalizaria conteúdo
            # antigo e verdadeiro. Fica sem achado, sem punir a cobertura.
            resultado.registrar(
                sem_achado(
                    "S-11",
                    "A busca funcionou e não achou nenhuma publicação semelhante. "
                    "Pode ser notícia muito nova, ou assunto que ninguém cobriu.",
                )
            )
            resultado.explicacao += (
                " Procurei e não encontrei outras publicações sobre o assunto. Isso "
                "pode ser notícia muito nova, ou assunto que ninguém cobriu."
            )
            return self.repassar(noticia)

        self._procurar_checagem_de_agencia(noticia.texto, relacionados, resultado)
        self._medir_corroboracao(relacionados, resultado)
        self._medir_originalidade(relacionados, resultado)
        resultado.fontes_citadas.extend(d.url for d in relacionados if d.url)
        # A N4 compara cada evidência com a alegação do texto; é a N3 que as recolhe.
        resultado.evidencias.extend(d.titulo for d in relacionados if d.titulo)

        return self.repassar(noticia)

    def _procurar_checagem_de_agencia(
        self, texto: str, relacionados: list[DocumentoRelacionado], resultado
    ) -> None:
        """RF-17 — alguma agência já checou esta alegação? Se sim, RN-01 decide.

        Sem isto a busca por palavra-chave fazia a notícia falsa ser *corroborada pelo
        próprio desmentido dela*: perguntada sobre uma alegação desmentida, a N3 achava
        as checagens do G1, do Aos Fatos e do Boatos, contava três veículos confiáveis
        publicando sobre o assunto e empurrava S-11 para o máximo.
        """
        checagem = checagens_publicadas.encontrar(
            texto,
            [(d.fonte, d.titulo) for d in relacionados],
        )
        if checagem is None:
            return

        resultado.veredito_agencia = checagem.veredito
        resultado.agencia = checagem.agencia
        _log.info(
            "N3: checagem de agência encontrada (%s, %s): %r",
            checagem.agencia,
            checagem.veredito,
            checagem.titulo,
        )

    def _medir_corroboracao(
        self, relacionados: list[DocumentoRelacionado], resultado: AnaliseResultado
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
        self, relacionados: list[DocumentoRelacionado], resultado: AnaliseResultado
    ) -> None:
        """S-13 — o texto é cópia quase literal de uma fonte não confiável?

        Similaridade altíssima com veículo confiável é replicação legítima de conteúdo
        de agência, e não penaliza. O sinal só aponta falsidade quando a quase-cópia
        vem de fora da base curada.

        Não achar quase-cópia deixa o sinal **indisponível**, e não 1,0. Antes era 1,0,
        e isso creditava 5 pontos de veracidade a toda checagem em que a busca trouxe
        qualquer coisa — inclusive a uma saudação. Comparar com os cinco documentos que
        o buscador devolveu não estabelece originalidade: só diz que entre aqueles cinco
        não havia cópia.
        """
        comparados = [d for d in relacionados if d.similaridade_textual]
        if not comparados:
            resultado.registrar(
                sem_achado(
                    "S-13",
                    "Não avalio originalidade com este buscador: ele devolve títulos e "
                    "relevância, não comparação entre os textos.",
                )
            )
            return

        quase_copias = [d for d in comparados if d.similaridade >= LIMIAR_DE_COPIA]
        if not quase_copias:
            resultado.registrar(
                sem_achado(
                    "S-13",
                    "Nenhuma das publicações encontradas é cópia quase literal deste "
                    "texto — o que não é o mesmo que atestar originalidade.",
                )
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
