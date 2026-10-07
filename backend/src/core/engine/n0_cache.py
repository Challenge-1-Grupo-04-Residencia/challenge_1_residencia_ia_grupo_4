from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import NoticiaRequest
from src.core.entities.signal import medir

# Importa o banco que você criou no passo anterior
from src.infrastructure.database import SessionLocal, ChecagemCache

class CamadaN0Cache(CamadaVerificacao):
    """N0 (Cache) - Corta caminho se a notícia já estiver no banco (RF-17)."""

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        resultado = noticia.resultado
        resultado.camada_atual = "N0"
        
        # Limpa espaços e quebras de linha em volta do texto que veio do Frontend
        texto_limpo = noticia.texto.strip() if noticia.texto else ""
        
        url_busca = noticia.url
        if not url_busca and texto_limpo.startswith("http"):
            url_busca = texto_limpo

        print(f"[DEBUG N0] URL extraída para busca: {url_busca}")

        if not url_busca:
            print("[DEBUG N0] Nenhuma URL detectada. Repassando para N2.")
            return self.repassar(noticia)

        try:
            with SessionLocal() as db:
                cache_hit = db.query(ChecagemCache).filter(ChecagemCache.url_agencia == url_busca).first()
                print(f"[DEBUG N0] Resultado da busca no banco: {cache_hit}")

                if cache_hit:
                    nota = 0.0 if cache_hit.veredicto.lower() == "falso" else 1.0
                    
                    # Força a barra de confiança no máximo para o Orquestrador parar!
                    resultado.registrar(
                        medir("S-00", nota, f"Checagem instantânea encontrada via {cache_hit.agencia}.")
                    )
                    
                    resultado.explicacao += (
                        f" A agência {cache_hit.agencia} já analisou este link "
                        f"e o veredicto oficial é: {cache_hit.veredicto}."
                    )
                    
                    # RETORNO IMEDIATO: Impede que a N2, N3 e N4 rodem!
                    return noticia
                    
        except Exception as e:
            print(f"[Aviso N0] Falha ao consultar o banco de dados: {e}")

        # Se não achou, passa a bola pra Camada N2 ter que trabalhar
        return self.repassar(noticia)