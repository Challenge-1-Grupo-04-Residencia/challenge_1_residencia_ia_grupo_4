from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import NoticiaRequest
from src.infrastructure.scraper import WebScraper

class CamadaLeitorLink(CamadaVerificacao):
    """
    Camada intermediária: se a entrada for só um link, ela acessa o site, 
    raspa a reportagem real e substitui o texto da notícia para a N2 poder ler (RF-18).
    """

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        texto_limpo = noticia.texto.strip() if noticia.texto else ""
        url_alvo = noticia.url

        if not url_alvo and texto_limpo.startswith("http"):
            url_alvo = texto_limpo

        # Se temos uma URL mas o texto atual é apenas a própria URL vazia
        if url_alvo and (texto_limpo == url_alvo or texto_limpo == ""):
            print("[Leitor de Links] Descobri que o usuário mandou só uma URL!")
            print("[Leitor de Links] Extraindo o texto real da notícia...")
            
            # Aqui chamamos o Scraper que acabou de nascer!
            texto_raspado = WebScraper.extrair_texto(url_alvo)
            
            if texto_raspado:
                # Mágica! A gente substitui a string burra do HTTP pelo texto real da reportagem
                noticia.texto = texto_raspado
                # Garantimos que a url fique salva direitinho pra referência
                noticia.url = url_alvo
                print("[Leitor de Links] Texto injetado com sucesso! N2 vai ler de barriga cheia.")
            else:
                print("[Leitor de Links] Não consegui raspar nada (Página bloqueada ou vazia).")
                noticia.resultado.explicacao += (
                    " Tentei ler a reportagem diretamente do link, mas o site original bloqueou "
                    "o acesso do meu leitor automatizado (isso é super comum em sites governamentais "
                    "ou portais com paywall). Por causa disso, eu não consegui avaliar o estilo de "
                    "escrita (N2) do texto original."
                )

        return self.repassar(noticia)
