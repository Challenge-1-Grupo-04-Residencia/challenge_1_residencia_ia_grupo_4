import urllib.parse
from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import NoticiaRequest
from src.core.entities.signal import medir
from src.infrastructure.database import SessionLocal, DominioReputacao

class CamadaN1Fonte(CamadaVerificacao):
    """N1 (Fonte) - Analisa o histórico criminal e a reputação de quem publicou (RF-18)."""

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        resultado = noticia.resultado
        resultado.camada_atual = "N1"
        
        # Puxa a URL (ou tenta achar no texto, igual fizemos na N0)
        url_alvo = noticia.url
        texto_limpo = noticia.texto.strip() if noticia.texto else ""
        if not url_alvo and texto_limpo.startswith("http"):
            url_alvo = texto_limpo

        if not url_alvo:
            print("[DEBUG N1] Nenhuma URL para avaliar reputação. Repassando para N2.")
            return self.repassar(noticia)

        try:
            # Extrai o domínio principal (ex: https://g1.globo.com/noticia -> g1.globo.com)
            dominio = urllib.parse.urlparse(url_alvo).netloc.lower()
            print(f"[DEBUG N1] Domínio extraído: {dominio}")

            with SessionLocal() as db:
                ficha = db.query(DominioReputacao).filter(DominioReputacao.dominio == dominio).first()
                
                if ficha:
                    # Converte o nosso score (0 a 100) para a métrica da Vera (0.0 a 1.0)
                    score_normalizado = ficha.score_confiabilidade / 100.0
                    
                    texto_justificativa = (
                        f"Veículo conhecido na base. Histórico: {ficha.noticias_verdadeiras} verdades "
                        f"e {ficha.noticias_falsas} fakes. Taxa de confiabilidade: {ficha.score_confiabilidade}%."
                    )
                    
                    # Registra o Sinal S-01 (Reputação na base curada)
                    resultado.registrar(medir("S-01", score_normalizado, texto_justificativa))
                    print(f"[DEBUG N1] Sinal S-01 aplicado com nota {score_normalizado}")
                else:
                    # Domínio desconhecido
                    print("[DEBUG N1] Domínio desconhecido. Marcando S-01 como nulo (baixa confiança).")
                    resultado.registrar(medir("S-01", None, "Domínio desconhecido na nossa base curada."))
                    
        except Exception as e:
            print(f"[Aviso N1] Falha ao consultar reputação da fonte: {e}")

        # Diferente da N0, a N1 não encerra a verificação! 
        # Ela apenas anota a reputação e repassa para a N2 olhar o estilo do texto.
        return self.repassar(noticia)
