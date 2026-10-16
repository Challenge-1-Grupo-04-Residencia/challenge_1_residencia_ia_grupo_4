import httpx
from bs4 import BeautifulSoup

class WebScraper:
    """Extrai o texto real de uma notícia a partir da sua URL."""
    
    @staticmethod
    def extrair_texto(url: str) -> str:
        """
        Acessa a URL, faz o download do HTML e extrai todos os parágrafos.
        Retorna o texto limpo da notícia.
        """
        try:
            # Headers falsos para fingir ser um navegador comum e evitar bloqueios (403 Forbidden)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            print(f"[Scraper] Fazendo download da página: {url}")
            
            # Timeout de 5s para não travar a Vera se o site for lento
            response = httpx.get(url, headers=headers, follow_redirects=True, timeout=5.0)
            response.raise_for_status()

            # Lxml é mais rápido e tolera HTML quebrado melhor que o html.parser nativo
            soup = BeautifulSoup(response.text, "lxml")

            # Remove tags inúteis (scripts, estilos, menus)
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extrai apenas os parágrafos reais (onde a notícia vive)
            paragrafos = soup.find_all("p")
            texto_extraido = "\n".join([p.get_text(strip=True) for p in paragrafos if p.get_text(strip=True)])

            if not texto_extraido:
                # Fallback: pega tudo que for texto se não tiver tags <p> claras
                texto_extraido = soup.get_text(separator="\n", strip=True)

            print(f"[Scraper] Sucesso! Extraídos {len(texto_extraido)} caracteres de texto.")
            return texto_extraido
            
        except Exception as e:
            print(f"[Scraper] Erro ao extrair texto da URL {url}: {e}")
            return ""
