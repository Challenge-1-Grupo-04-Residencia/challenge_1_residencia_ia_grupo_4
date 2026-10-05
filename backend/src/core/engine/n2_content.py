"""Camada N2 · Conteúdo — avalia **como** a notícia está escrita.

Mede os sinais da dimensão Conteúdo: o classificador estilístico treinado nos datasets
brasileiros (S-06, RF-21), sensacionalismo (S-07, RF-22), intensidade emocional
manipulativa (S-08, RF-23) e citação de fontes verificáveis (S-09, RF-24).

## Dois sinais que só podem descontar

S-07 e S-08 entram no cálculo com score no intervalo ``[0; 0,5]``, e não ``[0; 1]``.
Eles detectam **manipulação**: encontrar gritaria ou insulto é evidência contra a
notícia, mas *não* encontrar não é evidência a favor — mentira escrita em tom sóbrio
existe e é o caso difícil. Enquanto os dois podiam chegar a 1,0, somavam 10 dos 23
pontos ativos quase sempre no máximo, e o efeito medido foi que apenas 11,9% a 25% das
notícias falsas dos corpora caíam na faixa "provavelmente falsa": qualquer texto sem
berro era empurrado para cima. ``0,5`` é o ponto neutro da média ponderada, então um
sinal que vale 0,5 não mexe no score — é o que um detector silencioso deve fazer.

Quando o detector não encontra nada para medir, o sinal fica **indisponível** em vez de
valer o neutro: por RN-06 isso derruba a cobertura, que é a forma honesta de dizer "não
tenho leitura disso aqui".
"""

import os
from pathlib import Path

import joblib

from src.core.engine import emotion, text_style
from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import AnaliseResultado, NoticiaRequest
from src.core.entities.signal import medir

#: Resolvido a partir da localização deste arquivo, e não do diretório de trabalho: o
#: caminho relativo antigo só funcionava quando o servidor subia da raiz do repositório.
CAMINHO_MODELO_PADRAO = str(
    Path(__file__).resolve().parents[2]
    / "infrastructure"
    / "ml_models"
    / "classificador_n2.joblib"
)

#: Abaixo deste número de palavras nenhum sinal de estilo é confiável: não há texto
#: suficiente para a assinatura aparecer, nem para esperar que um trecho cite fonte.
MINIMO_DE_PALAVRAS = 10

#: Teto dos sinais que só detectam manipulação. Ver o cabeçalho do módulo.
TETO_DOS_DETECTORES = 0.5


class CamadaN2Conteudo(CamadaVerificacao):
    """Analisa estilo, sensacionalismo, carga emocional e ancoragem em fontes."""

    def __init__(self, caminho_modelo: str = CAMINHO_MODELO_PADRAO):
        super().__init__()
        self.caminho_modelo = caminho_modelo
        self.modelo = None
        self._carregar_modelo()

    def _carregar_modelo(self) -> None:
        if os.path.exists(self.caminho_modelo):
            self.modelo = joblib.load(self.caminho_modelo)
        else:
            print(
                f"[Aviso] Modelo não encontrado em {self.caminho_modelo}. "
                "Execute o notebook de EDA N2 para gerá-lo."
            )

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        resultado = noticia.resultado
        resultado.camada_atual = "N2"
        texto = noticia.texto.strip()
        texto_curto = len(texto.split()) < MINIMO_DE_PALAVRAS

        self._medir_estilo(texto, resultado, texto_curto)
        self._medir_sensacionalismo(texto, resultado)
        self._medir_intensidade_emocional(texto, resultado)
        self._medir_citacao_de_fontes(texto, resultado, texto_curto)

        return self.repassar(noticia)

    def _medir_estilo(
        self, texto: str, resultado: AnaliseResultado, texto_curto: bool
    ) -> None:
        """S-06 — probabilidade de a notícia ser verdadeira, segundo o classificador."""
        if texto_curto:
            resultado.registrar(
                medir(
                    "S-06",
                    None,
                    "Texto curto demais para uma análise de estilo confiável.",
                )
            )
            resultado.explicacao += (
                " Texto muito curto para análise de estilo (S-06 indisponível)."
            )
            return

        if self.modelo is None:
            resultado.registrar(
                medir("S-06", None, "Classificador de estilo não carregado.")
            )
            return

        probabilidades = self.modelo.predict_proba([texto])[0]
        classes = list(self.modelo.classes_)
        prob_verdadeiro = self._probabilidade_de_verdadeiro(probabilidades, classes)

        resultado.registrar(
            medir(
                "S-06",
                prob_verdadeiro,
                f"O classificador estilístico dá {prob_verdadeiro * 100:.0f}% "
                "de chance de o texto ser verdadeiro.",
            )
        )
        if prob_verdadeiro < 0.4:
            resultado.explicacao += (
                f" Detectado estilo de escrita apelativo/falso "
                f"({(1 - prob_verdadeiro) * 100:.1f}% de chance)."
            )
        else:
            resultado.explicacao += " Estilo de escrita não aparenta ser sensacionalista."

    @staticmethod
    def _probabilidade_de_verdadeiro(probabilidades, classes: list) -> float:
        """Extrai P(verdadeiro) sem depender da ordem das classes do modelo.

        Os notebooks de EDA rotularam as classes de formas diferentes ao longo do
        projeto, então o nome é procurado entre as variantes conhecidas antes de cair
        no complemento de P(falso).
        """
        for rotulo in ("verdadeiro", "verdadeira", "true", "real", 1):
            if rotulo in classes:
                return float(probabilidades[classes.index(rotulo)])
        for rotulo in ("falso", "falsa", "fake", "false", 0):
            if rotulo in classes:
                return 1.0 - float(probabilidades[classes.index(rotulo)])
        # Sem rótulo reconhecível, assume a convenção do scikit-learn: índice 1 é a
        # classe positiva.
        return float(probabilidades[-1])

    def _medir_sensacionalismo(self, texto: str, resultado: AnaliseResultado) -> None:
        """S-07 — gritaria e pedido de difusão (RF-22)."""
        indice = text_style.indice_sensacionalismo(texto)
        if indice is None:
            resultado.registrar(
                medir(
                    "S-07",
                    None,
                    "Não encontrei marcas de sensacionalismo para medir.",
                )
            )
            return

        resultado.registrar(
            medir(
                "S-07",
                self._desconto(indice),
                f"Índice de sensacionalismo {indice:.2f}: pontuação repetida e "
                "vocabulário de urgência pedindo difusão.",
            )
        )
        resultado.explicacao += " O texto usa linguagem de urgência e pede repasse."

    def _medir_intensidade_emocional(
        self, texto: str, resultado: AnaliseResultado
    ) -> None:
        """S-08 — vocabulário de degradação moral usado para gerar indignação (RF-23)."""
        indice, emocao = emotion.indice_intensidade_emocional(texto)
        if indice is None:
            resultado.registrar(
                medir(
                    "S-08",
                    None,
                    "O texto não traz vocabulário emocional manipulativo para medir.",
                )
            )
            return

        resultado.registrar(
            medir(
                "S-08",
                self._desconto(indice),
                f"Detectada carga emocional de {emocao} em {indice * 100:.0f}% "
                "da escala: o texto desqualifica pessoas em vez de argumentar.",
            )
        )
        resultado.explicacao += (
            f" O texto carrega na emoção ({emocao}) para convencer."
        )

    def _medir_citacao_de_fontes(
        self, texto: str, resultado: AnaliseResultado, texto_curto: bool
    ) -> None:
        """S-09 — o texto ancora o que afirma em links ou órgãos nomeados?"""
        if texto_curto:
            resultado.registrar(
                medir(
                    "S-09",
                    None,
                    "Texto curto demais para esperar citação de fontes.",
                )
            )
            return

        indice = text_style.indice_citacao_de_fontes(texto)
        resultado.registrar(
            medir(
                "S-09",
                indice,
                "O texto não cita fontes verificáveis."
                if indice == 0
                else f"O texto traz citações verificáveis (índice {indice:.2f}).",
            )
        )

    @staticmethod
    def _desconto(indice: float) -> float:
        """Converte índice de manipulação em score que só consegue puxar para baixo.

        ``indice`` 0 viraria o neutro 0,5 e ``indice`` 1 vira 0: o sinal desconta no
        máximo metade do seu peso e nunca credita veracidade a um texto só por ele não
        ter gritado.
        """
        return TETO_DOS_DETECTORES * (1.0 - indice)
