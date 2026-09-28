import os
import joblib
from src.core.entities.claim import NoticiaRequest
from src.core.engine.orchestrator import CamadaVerificacao

class CamadaN2Conteudo(CamadaVerificacao):
    """
    Camada N2: Analisa o estilo e o sensacionalismo do texto.
    Atende à [US] Detecção de estilo falso (RF-21) e [US] Alerta de sensacionalismo (RF-22).
    """
    def __init__(self, caminho_modelo: str = "src/infrastructure/ml_models/classificador_n2.joblib"):
        super().__init__()
        self.caminho_modelo = caminho_modelo
        self.modelo = None
        self._carregar_modelo()

    def _carregar_modelo(self):
        if os.path.exists(self.caminho_modelo):
            self.modelo = joblib.load(self.caminho_modelo)
        else:
            print(f"[Aviso] Modelo não encontrado em {self.caminho_modelo}. Execute o notebook de EDA N2 para gerá-lo.")

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        # Atualiza a camada atual
        noticia.resultado.camada_atual = "N2"
        
        texto = noticia.texto.strip()
        
        # Regra do critério de aceite: se o texto for muito curto, pula a classificação de ML
        if len(texto.split()) < 10:
            noticia.resultado.explicacao += " Texto muito curto para análise de estilo (N2 pulada)."
            # Repassa para N3/N4
            return self.repassar(noticia)

        if self.modelo:
            # Predict Proba retorna [Prob_Falso, Prob_Verdadeiro] dependendo de como foi treinado.
            # Baseado na EDA, a classe "falso" geralmente é a probabilidade que buscamos punir.
            probabilidades = self.modelo.predict_proba([texto])[0]
            classes = self.modelo.classes_
            
            # Mapeando qual index é 'falso' e qual é 'verdadeiro'
            idx_falso = list(classes).index("falso") if "falso" in classes else 0
            prob_falso = probabilidades[idx_falso]
            
            # Calcula impacto na veracidade e confiança
            # Se prob_falso é altíssima (ex: > 80%), veracidade cai.
            if prob_falso > 0.6:
                noticia.resultado.veracidade -= (prob_falso * 20)  # Punição no score base
                noticia.resultado.explicacao += f" Detectado estilo de escrita apelativo/falso ({prob_falso*100:.1f}% de chance)."
                noticia.resultado.confianca += 0.2 # Aumentamos um pouco a confiança pois achamos um sinal
            else:
                noticia.resultado.explicacao += " Estilo de escrita não aparenta ser sensacionalista."
        
        # Padrão Chain of Responsibility: verifica se já pode parar ou repassa
        return self.repassar(noticia)
