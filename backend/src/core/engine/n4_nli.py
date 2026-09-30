"""Camada N4 · LLM — inferência lógica de evidências (RF-30).

Última e mais cara camada: compara cada evidência recolhida pela N3 com a alegação do
texto e pergunta se ela **sustenta**, **contradiz** ou é **neutra**. Mede S-12, que com
peso 20 é o sinal mais pesado do catálogo — é o único que olha o conteúdo das
evidências em vez de apenas contá-las.

Por RN-07 esta camada só roda se N0 a N3 não atingiram a regra de parada.
"""

from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import NoticiaRequest
from src.core.entities.signal import medir

#: Modelo multilíngue de NLI com suporte a português.
MODELO_NLI = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

#: Abaixo desta confiança o rótulo do modelo não é levado em conta. NLI em português
#: erra com frequência em textos jornalísticos longos, e um veredito fraco não deve
#: mover o sinal mais pesado do catálogo.
CONFIANCA_MINIMA_NLI = 0.6

_classificador = None


def obter_classificador():
    """Carrega o modelo na primeira chamada.

    A inicialização é preguiçosa de propósito: o mDeBERTa leva dezenas de segundos para
    carregar e travaria a subida do servidor, mesmo nas requisições que nunca chegam à
    N4 — que devem ser a maioria.
    """
    global _classificador
    if _classificador is None:
        try:
            from transformers import pipeline
        except ImportError as erro:
            # O extra é opcional porque traz o torch (~2 GB); sem a mensagem explícita
            # o erro apareceria como um ImportError cru no meio de uma requisição.
            raise RuntimeError(
                "A camada N4 precisa do extra 'nli'. Instale com: uv sync --extra nli"
            ) from erro

        print("Carregando modelo de Inferência Lógica (NLI) na memória...")
        _classificador = pipeline("text-classification", model=MODELO_NLI)
    return _classificador


class CamadaN4Inferencia(CamadaVerificacao):
    """Avalia se as evidências da N3 sustentam ou contradizem a alegação."""

    def __init__(self, classificador=None):
        super().__init__()
        # Injetável para que o teste rode sem baixar o modelo.
        self._classificador = classificador

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        resultado = noticia.resultado
        resultado.camada_atual = "N4"

        if not resultado.evidencias:
            # Sem evidência não há o que inferir. O sinal fica indisponível (RN-06) em
            # vez de zero: não conseguir julgar não é julgar que a notícia é falsa.
            resultado.registrar(
                medir("S-12", None, "A N3 não trouxe evidências para comparar.")
            )
            resultado.explicacao += " Não achei material suficiente para conferir alegação por alegação."
            return self.repassar(noticia)

        sustentam, contradizem = self._inferir(noticia.texto, resultado.evidencias)

        decisivas = sustentam + contradizem
        if decisivas == 0:
            resultado.registrar(
                medir(
                    "S-12",
                    None,
                    "As evidências são neutras: nenhuma sustenta nem contradiz a alegação.",
                )
            )
            resultado.explicacao += " As publicações que achei não confirmam nem desmentem isso."
            return self.repassar(noticia)

        # Fórmula de S-12 na documentação: sustenta / (sustenta + contradiz).
        score = sustentam / decisivas
        resultado.registrar(
            medir(
                "S-12",
                score,
                f"Das evidências conclusivas, {sustentam} sustentam e "
                f"{contradizem} contradizem a alegação.",
            )
        )
        resultado.explicacao += (
            f" Conferi alegação por alegação: {sustentam} evidência(s) sustentam e "
            f"{contradizem} contradizem."
        )

        return self.repassar(noticia)

    def _inferir(self, alegacao: str, evidencias: list[str]) -> tuple[int, int]:
        """Conta quantas evidências sustentam e quantas contradizem a alegação.

        O modelo recebe a evidência como premissa e a alegação como hipótese — nesta
        ordem, porque a pergunta é se a evidência publicada implica a alegação do texto,
        não o contrário.
        """
        classificador = self._classificador or obter_classificador()
        sustentam = 0
        contradizem = 0

        for evidencia in evidencias:
            veredito = classificador({"text": evidencia, "text_pair": alegacao})
            rotulo = veredito["label"].lower()
            confianca = veredito["score"]

            if confianca <= CONFIANCA_MINIMA_NLI:
                continue
            if "entailment" in rotulo:
                sustentam += 1
            elif "contradiction" in rotulo:
                contradizem += 1

        return sustentam, contradizem
