import os
from src.core.entities.claim import NoticiaRequest
from src.core.engine.orchestrator import CamadaVerificacao

# Inicialização lazy do modelo para não travar a subida do servidor
_nli_classifier = None

def get_nli_classifier():
    global _nli_classifier
    if _nli_classifier is None:
        from transformers import pipeline
        # Modelo mDeBERTa otimizado para NLI e Zero-Shot em várias linguagens (incluindo Português)
        print("Carregando modelo de Inferência Lógica (NLI) na memória...")
        _nli_classifier = pipeline("text-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
    return _nli_classifier

class CamadaN4Inferencia(CamadaVerificacao):
    """
    Camada N4: Inferência Lógica de Evidências (NLI)
    Avalia se as evidências coletadas pela N3 corroboram ou refutam a notícia original.
    """
    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        noticia.resultado.camada_atual = "N4"
        
        # Se não há evidências (N3 falhou ou não achou nada), não temos como julgar
        if not noticia.resultado.evidencias:
            noticia.resultado.explicacao += " [N4 ignorada: Nenhuma evidência fornecida pela N3]."
            return self.repassar(noticia)

        classifier = get_nli_classifier()
        hipotese = noticia.texto

        corroboracoes = 0
        refutacoes = 0
        
        # O NLI compara a Notícia (Hipótese) contra cada Texto da Internet (Premissa)
        for evidencia in noticia.resultado.evidencias:
            # O HuggingFace aceita um par {"text": premissa, "text_pair": hipotese} para NLI
            resultado_nli = classifier({"text": evidencia, "text_pair": hipotese})
            
            label = resultado_nli['label'].lower()
            score = resultado_nli['score']
            
            if "entailment" in label and score > 0.6:
                corroboracoes += 1
            elif "contradiction" in label and score > 0.6:
                refutacoes += 1

        # Lógica de Decisão do Juiz Final (N4)
        if refutacoes > corroboracoes:
            noticia.resultado.veracidade = max(0.0, noticia.resultado.veracidade - 30)
            noticia.resultado.confianca += 0.4
            noticia.resultado.explicacao += f" [N4: Evidências REFUTAM a notícia ({refutacoes} refutações contra {corroboracoes} corroborações)]."
        elif corroboracoes > refutacoes:
            noticia.resultado.veracidade = min(100.0, noticia.resultado.veracidade + 30)
            noticia.resultado.confianca += 0.4
            noticia.resultado.explicacao += f" [N4: Evidências CORROBORAM a notícia ({corroboracoes} a favor)]."
        else:
            noticia.resultado.explicacao += " [N4: Evidências Neutras ou Inconclusivas]."

        return self.repassar(noticia)
