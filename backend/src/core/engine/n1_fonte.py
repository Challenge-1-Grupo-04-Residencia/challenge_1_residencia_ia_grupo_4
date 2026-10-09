import urllib.parse
from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import NoticiaRequest
from src.infrastructure.database import SessionLocal, DominioReputacao
from src.core.entities.signal import medir, nao_medido
from src.infrastructure.whois_client import consultar_idade_meses

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
                    # --- INÍCIO DO CÁLCULO S-03 (Idade do Domínio) ---
        try:
            idade_meses = consultar_idade_meses(dominio)
            
            if idade_meses is not None:
                # Se tiver menos de 6 meses, penalizamos (score 0.0)
                if idade_meses < 6:
                    resultado.registrar(medir("S-03", 0.0, f"Domínio suspeito: registro muito recente ({idade_meses} meses)."))
                    print(f"[DEBUG N1] Sinal S-03 aplicado com nota 0.0 (Recente)")
                else:
                    resultado.registrar(medir("S-03", 1.0, f"Domínio antigo e estabelecido ({idade_meses} meses)."))
                    print(f"[DEBUG N1] Sinal S-03 aplicado com nota 1.0 (Antigo)")
            else:
                # Falha na API ou falta de chave não deve derrubar a nota injustamente
                print("[DEBUG N1] Idade não encontrada ou WHOIS indisponível. Marcando S-03 como não medido.")
                resultado.registrar(nao_medido("S-03", "Não foi possível consultar a idade do domínio (WHOIS falhou)."))
        
        except Exception as e:
            print(f"[Aviso N1] Erro crítico ao processar o S-03: {e}")
            resultado.registrar(nao_medido("S-03", "Erro interno ao validar WHOIS."))
        # --- FIM DO CÁLCULO S-03 ---

        # Diferente da N0, a N1 não encerra a verificação! 
        # Ela apenas anota a reputação e repassa para a N2 olhar o estilo do texto.
        return self.repassar(noticia)
