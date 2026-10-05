"""Camada N4 · LLM — inferência lógica de evidências (RF-30).

Última e mais cara camada: compara as evidências recolhidas pela N3 com a alegação do
texto e pergunta se elas **sustentam**, **contradizem** ou são **neutras**. Mede S-12, que com
peso 20 é o sinal mais pesado do catálogo — é o único que olha o conteúdo das
evidências em vez de apenas contá-las.

Por RN-07 esta camada só roda se N0 a N3 não atingiram a regra de parada.
"""

import json
import os
import urllib.request

from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import NoticiaRequest
from src.core.entities.signal import medir

def chamada_ollama_real(prompt: str) -> dict:
    """Faz a chamada HTTP real para o Llama 3 via Ollama."""
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    req = urllib.request.Request(f"{ollama_url}/api/generate", method="POST")
    req.add_header('Content-Type', 'application/json')
    
    data = json.dumps({
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }).encode('utf-8')
    
    try:
        response = urllib.request.urlopen(req, data=data, timeout=60)
        result = json.loads(response.read().decode('utf-8'))
        return json.loads(result['response'])
    except Exception as e:
        return {"veredicto": "NEUTRAL", "explicacao": f"Erro na API Ollama: {str(e)}"}


class CamadaN4Inferencia(CamadaVerificacao):
    """Avalia se as evidências da N3 sustentam ou contradizem a alegação usando Llama 3."""

    def __init__(self, api_client=None):
        super().__init__()
        # Injetável para que o PyTest rode sem precisar de uma GPU/Ollama real rodando.
        self._api_client = api_client or chamada_ollama_real

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        resultado = noticia.resultado
        resultado.camada_atual = "N4"

        if not resultado.evidencias:
            resultado.registrar(
                medir("S-12", None, "A N3 não trouxe evidências para comparar.")
            )
            resultado.explicacao += " Não achei material suficiente para conferir alegação por alegação."
            return self.repassar(noticia)

        sustentam, contradizem, explicacao_llm = self._inferir(noticia.texto, resultado.evidencias)

        decisivas = sustentam + contradizem
        if decisivas == 0:
            resultado.registrar(
                medir(
                    "S-12",
                    None,
                    f"As evidências são neutras: {explicacao_llm}",
                )
            )
            resultado.explicacao += f" As publicações que achei não confirmam nem desmentem isso. (IA: {explicacao_llm})"
            return self.repassar(noticia)

        score = sustentam / decisivas
        resultado.registrar(
            medir(
                "S-12",
                score,
                f"Das evidências analisadas, o modelo julgou: {explicacao_llm}",
            )
        )
        
        veredito = "sustentam" if sustentam > contradizem else "contradizem"
        resultado.explicacao += f" Conferi o conteúdo: as evidências {veredito} a notícia. (IA: {explicacao_llm})"

        return self.repassar(noticia)

    def _inferir(self, alegacao: str, evidencias: list[str]) -> tuple[int, int, str]:
        """Faz uma chamada única ao Ollama para avaliar todas as evidências em bloco.
        Isso reduz drasticamente a latência em comparação com 1 chamada por evidência."""
        
        evidencias_texto = "\n".join([f"- {ev}" for ev in evidencias])
        
        prompt = f"""Você é um juiz de Fact-Checking avançado.
Analise a Notícia original e compare com as Evidências fornecidas.
ATENÇÃO: Você possui conhecimento de mundo. Use-o para resolver sinônimos (ex: e-scooters = patinetes elétricos) e fatos geográficos (ex: Paris = capital da França). Não seja excessivamente literal; julgue o significado real.

Notícia original: {alegacao}

Evidências coletadas na internet:
{evidencias_texto}

Responda EXATAMENTE no formato JSON abaixo, sem usar formatação markdown e sem texto adicional:
{{"veredicto": "...", "explicacao": "motivo resumido"}}

REGRAS ESTRITAS DO VEREDICTO:
- ENTAILMENT: As evidências confirmam a notícia (mesmo usando palavras diferentes ou sinônimos).
- CONTRADICTION: As evidências provam que a notícia é falsa (ex: números ou dados conflitantes sobre o mesmo evento).
- NEUTRAL: As evidências NÃO abordam a notícia ou falam de coisas diferentes. Omissão de dados = NEUTRAL.

ATENÇÃO AO NEUTRAL: Se a evidência fala de "carros" e a notícia de "bicicletas", ISSO É NEUTRAL, pois a evidência simplesmente não tocou no assunto das bicicletas. Não use ausência de informação como contradição!
"""

        resposta = self._api_client(prompt)
        veredicto = resposta.get("veredicto", "NEUTRAL").upper()
        explicacao = resposta.get("explicacao", "Sem explicação detalhada.")

        # Traduz a saída do Llama para a matemática do motor (S-12)
        if any(palavra in veredicto for palavra in ["ENTAILMENT", "VERDADEIRO", "SUSTENTA", "CONFIRMA", "TRUE"]):
            return 1, 0, explicacao
        elif any(palavra in veredicto for palavra in ["CONTRADICTION", "FALSO", "CONTRADIZ", "MENTIRA", "FALSE"]):
            return 0, 1, explicacao
        else:
            return 0, 0, explicacao
