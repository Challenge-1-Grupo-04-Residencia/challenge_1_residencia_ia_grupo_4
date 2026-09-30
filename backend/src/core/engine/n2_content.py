"""Camada N2 · Conteúdo — avalia **como** a notícia está escrita.

Mede os sinais da dimensão Conteúdo (25 pontos): o classificador estilístico treinado
nos datasets brasileiros (S-06, RF-21), sensacionalismo (S-07, RF-22) e citação de
fontes verificáveis (S-09, RF-24).

S-08 (intensidade emocional, RF-23) depende do NRC Emotion Lexicon, que ainda não foi
integrado. A camada deixa o sinal indisponível em vez de chutar: por RN-06 ele sai do
cálculo e apenas reduz a cobertura, o que é honesto — o contrário seria inventar uma
medição e inflar a confiança.
"""

import os

import joblib

from src.core.engine import text_style
from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import NoticiaRequest
from src.core.entities.signal import medir

CAMINHO_MODELO_PADRAO = "backend/src/infrastructure/ml_models/classificador_n2.joblib"

#: Abaixo deste número de palavras o classificador estilístico não é confiável: não há
#: texto suficiente para a assinatura de estilo aparecer.
MINIMO_DE_PALAVRAS = 10


class CamadaN2Conteudo(CamadaVerificacao):
    """Analisa estilo, sensacionalismo e ancoragem em fontes."""

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

        self._medir_estilo(texto, resultado)
        self._medir_sensacionalismo(texto, resultado)
        self._medir_citacao_de_fontes(texto, resultado)

        return self.repassar(noticia)

    def _medir_estilo(self, texto: str, resultado) -> None:
        """S-06 — probabilidade de a notícia ser verdadeira, segundo o classificador."""
        if len(texto.split()) < MINIMO_DE_PALAVRAS:
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

    def _medir_sensacionalismo(self, texto: str, resultado) -> None:
        """S-07 — o score é o inverso do índice: quanto mais grita, menor a nota."""
        indice = text_style.indice_sensacionalismo(texto)
        resultado.registrar(
            medir(
                "S-07",
                1.0 - indice,
                f"Índice de sensacionalismo {indice:.2f} "
                "(caixa alta, pontuação repetida e vocabulário de urgência).",
            )
        )

    def _medir_citacao_de_fontes(self, texto: str, resultado) -> None:
        """S-09 — o texto ancora o que afirma em links ou órgãos nomeados?"""
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
