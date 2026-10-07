"""Camada N4 · LLM — inferência lógica sobre as evidências (RF-30, S-12).

Última e mais cara camada: compara cada evidência recolhida pela N3 com a alegação do
texto e pergunta se ela **sustenta**, **contradiz** ou é **neutra**. Mede S-12, que com
peso 20 é o sinal mais pesado do catálogo — o único que olha o *conteúdo* das evidências
em vez de apenas contá-las.

Por RN-07 esta camada só roda se N0 a N3 não atingiram a regra de parada.

## Um veredito por evidência, numa única chamada

A versão anterior pedia **um** veredito para o bloco inteiro de evidências. Como o score
de S-12 é ``sustentam / (sustentam + contradizem)``, um veredito único só podia dar 1,0
ou 0,0: o sinal mais pesado do catálogo virou moeda. Medido na mesma notícia verdadeira,
a diferença entre o modelo responder ENTAILMENT ou CONTRADICTION era de **32 pontos** no
score final (85,0 "Confirmada por fontes" contra 53,3 "Inconclusiva").

Agora o modelo devolve uma lista, um veredito por evidência, na mesma chamada — então a
latência continua sendo de uma requisição e o score volta a ser gradiente: três
evidências que sustentam e uma que contradiz dão 0,75, e não 1,0.

## Falha de provedor não é evidência

Se o Ollama não responde, S-12 fica **indisponível** (RN-06) e a explicação diz que a
conferência não foi possível. Antes, o erro de rede era convertido em veredito NEUTRAL e
o usuário lia na voz da Vera o texto ``Erro na API Ollama: <urlopen error [Errno 61]
Connection refused>`` — detalhe técnico vazado numa frase de persona, o que quebra RN-11
e apresenta uma falha nossa como achado sobre a notícia dele.
"""

import json
import logging
import os
import urllib.error
import urllib.request

from src.core.engine.orchestrator import CamadaVerificacao
from src.core.entities.claim import AnaliseResultado, NoticiaRequest
from src.core.entities.signal import medir, nao_medido, sem_achado

_log = logging.getLogger(__name__)

#: Teto de evidências enviadas numa chamada. Acima disso o prompt fica longo, o modelo
#: começa a truncar a lista de vereditos e o ganho de informação é marginal.
MAXIMO_DE_EVIDENCIAS = 8

ROTULO_SUSTENTA = "ENTAILMENT"
ROTULO_CONTRADIZ = "CONTRADICTION"
ROTULO_NEUTRO = "NEUTRAL"


class ErroDoProvedor(Exception):
    """O provedor de LLM não respondeu, ou respondeu algo que não dá para usar.

    Existe para a camada poder distinguir "o modelo disse que as evidências são
    neutras" de "não consegui falar com o modelo". As duas coisas chegavam aqui como a
    mesma resposta NEUTRAL, e a segunda não é informação sobre a notícia.
    """


def chamada_ollama_real(prompt: str) -> dict:
    """Chamada HTTP ao modelo servido pelo Ollama.

    Levanta :class:`ErroDoProvedor` em qualquer falha, em vez de devolver um veredito
    fabricado.
    """
    url_base = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    modelo = os.environ.get("OLLAMA_MODEL", "llama3")
    timeout = float(os.environ.get("OLLAMA_TIMEOUT", "30"))

    requisicao = urllib.request.Request(f"{url_base}/api/generate", method="POST")
    requisicao.add_header("Content-Type", "application/json")
    corpo = json.dumps(
        {"model": modelo, "prompt": prompt, "stream": False, "format": "json"}
    ).encode("utf-8")

    try:
        with urllib.request.urlopen(requisicao, corpo, timeout=timeout) as resposta:
            envelope = json.loads(resposta.read().decode("utf-8"))
        return json.loads(envelope["response"])
    except (urllib.error.URLError, OSError) as erro:
        raise ErroDoProvedor(f"não foi possível falar com o Ollama: {erro}") from erro
    except (json.JSONDecodeError, KeyError, TypeError) as erro:
        raise ErroDoProvedor(f"resposta do Ollama ilegível: {erro}") from erro


class CamadaN4Inferencia(CamadaVerificacao):
    """Avalia se as evidências da N3 sustentam ou contradizem a alegação."""

    nome = "N4"

    def __init__(self, api_client=None):
        super().__init__()
        # Injetável para que os testes rodem sem Ollama no ar — por convenção do
        # projeto, teste não toca a rede.
        self._api_client = api_client or chamada_ollama_real

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        resultado = noticia.resultado
        resultado.camada_atual = "N4"

        if not resultado.evidencias:
            # Sem evidência não há o que inferir, e a ausência de publicação já está
            # refletida em S-11: contar de novo aqui puniria a mesma lacuna duas vezes.
            resultado.registrar(
                sem_achado("S-12", "A N3 não trouxe evidências para comparar.")
            )
            resultado.explicacao += (
                " Não achei material suficiente para conferir alegação por alegação."
            )
            return self.repassar(noticia)

        evidencias = resultado.evidencias[:MAXIMO_DE_EVIDENCIAS]
        try:
            vereditos = self._inferir(noticia.texto, evidencias)
        except ErroDoProvedor as erro:
            # O detalhe técnico vai para o log, não para o usuário.
            _log.warning("N4 indisponível: %s", erro)
            resultado.registrar(
                nao_medido(
                    "S-12",
                    "A conferência por inferência não pôde ser feita: o provedor de "
                    "modelo não respondeu.",
                )
            )
            resultado.explicacao += (
                " Não consegui fazer a conferência fina das evidências agora — isso "
                "é limitação minha, não achado sobre a notícia."
            )
            return self.repassar(noticia)

        self._registrar_s12(vereditos, resultado)
        return self.repassar(noticia)

    def _registrar_s12(
        self, vereditos: list[tuple[str, str]], resultado: AnaliseResultado
    ) -> None:
        """Converte os vereditos por evidência no score de S-12."""
        sustentam = sum(1 for rotulo, _ in vereditos if rotulo == ROTULO_SUSTENTA)
        contradizem = sum(1 for rotulo, _ in vereditos if rotulo == ROTULO_CONTRADIZ)
        decisivas = sustentam + contradizem

        if not vereditos:
            resultado.registrar(
                nao_medido(
                    "S-12",
                    "O modelo não devolveu nenhum veredito utilizável.",
                )
            )
            resultado.explicacao += (
                " Não consegui fazer a conferência fina das evidências agora."
            )
            return

        if decisivas == 0:
            # Neutro não é meio-termo entre sustentar e contradizer: é ausência de dado.
            # O modelo leu e julgou: as evidências não tocam na alegação. Medição
            # feita, nada decisivo a anotar.
            resultado.registrar(
                sem_achado(
                    "S-12",
                    f"As {len(vereditos)} evidências analisadas são neutras: falam de "
                    "outro assunto e não tocam na alegação.",
                )
            )
            resultado.explicacao += (
                " As publicações que achei não confirmam nem desmentem isso."
            )
            return

        score = sustentam / decisivas
        resultado.registrar(
            medir(
                "S-12",
                score,
                f"De {len(vereditos)} evidências conferidas, {sustentam} sustentam a "
                f"alegação e {contradizem} a contradizem"
                + (
                    f" ({len(vereditos) - decisivas} não tratam do assunto)."
                    if len(vereditos) > decisivas
                    else "."
                ),
            )
        )
        if sustentam > contradizem:
            resultado.explicacao += (
                " Conferi o conteúdo: as evidências sustentam a notícia."
            )
        elif contradizem > sustentam:
            resultado.explicacao += (
                " Conferi o conteúdo: as evidências contradizem a notícia."
            )
        else:
            resultado.explicacao += (
                " Conferi o conteúdo e as evidências se dividem: há publicação dos "
                "dois lados."
            )

    def _inferir(self, alegacao: str, evidencias: list[str]) -> list[tuple[str, str]]:
        """Pede um veredito por evidência numa única chamada.

        Devolve a lista de ``(rótulo, motivo)``. Evidência cujo veredito veio ilegível é
        descartada em vez de contada como neutra, para não inventar medição.
        """
        numeradas = "\n".join(
            f"{i}. {evidencia}" for i, evidencia in enumerate(evidencias)
        )
        prompt = f"""Você é um juiz de fact-checking. Compare a notícia com CADA evidência, uma por uma.

Use conhecimento de mundo para resolver sinônimos (e-scooters = patinetes elétricos) e
fatos geográficos (Paris = capital da França). Julgue o significado real, não a letra.

NOTÍCIA: {alegacao}

EVIDÊNCIAS:
{numeradas}

Responda só com JSON, sem markdown, com um item para CADA evidência:
{{"vereditos": [{{"indice": 0, "veredicto": "{ROTULO_SUSTENTA}", "motivo": "resumo curto"}}]}}

REGRAS DO VEREDICTO, por evidência:
- {ROTULO_SUSTENTA}: a evidência confirma a notícia, mesmo com outras palavras.
- {ROTULO_CONTRADIZ}: a evidência prova que a notícia é falsa (ex.: números
  conflitantes sobre o mesmo evento).
- {ROTULO_NEUTRO}: a evidência não trata do assunto da notícia. Omissão é
  {ROTULO_NEUTRO}, nunca {ROTULO_CONTRADIZ}: se a evidência fala de carros e a notícia
  de bicicletas, é {ROTULO_NEUTRO}.

ATENÇÃO À NEGAÇÃO. Manchete de checagem cita a alegação inteira para desmenti-la, e
conter as mesmas palavras NÃO é confirmar:
- "É #FAKE que X" → a evidência diz que X é falso → {ROTULO_CONTRADIZ}
- "É falso que X" → {ROTULO_CONTRADIZ}
- "Fulano NÃO fez X" quando a notícia diz que fulano fez X → {ROTULO_CONTRADIZ}
Leia o que a frase afirma, não quais palavras ela repete.
"""
        resposta = self._api_client(prompt)
        return self._ler_vereditos(resposta)

    @staticmethod
    def _ler_vereditos(resposta) -> list[tuple[str, str]]:
        """Extrai os pares (rótulo, motivo) de uma resposta possivelmente malformada.

        Modelos pequenos erram o formato com frequência, e a tolerância aqui é
        deliberada: aceita a lista em ``vereditos`` ou a resposta já como lista, e
        aceita o formato antigo de veredito único. O que não dá para ler é descartado,
        porque contar como neutro seria fabricar uma medição.
        """
        if isinstance(resposta, dict):
            itens = resposta.get("vereditos")
            if itens is None:
                # Formato de veredito único: um rótulo para o bloco todo.
                rotulo = str(resposta.get("veredicto", "")).upper()
                motivo = str(resposta.get("explicacao", ""))
                itens = [{"veredicto": rotulo, "motivo": motivo}] if rotulo else []
        elif isinstance(resposta, list):
            itens = resposta
        else:
            raise ErroDoProvedor(f"formato inesperado: {type(resposta).__name__}")

        if not isinstance(itens, list):
            raise ErroDoProvedor("campo 'vereditos' não é uma lista")

        vereditos: list[tuple[str, str]] = []
        for item in itens:
            if not isinstance(item, dict):
                continue
            bruto = str(item.get("veredicto") or item.get("veredito") or "").upper()
            motivo = str(item.get("motivo") or item.get("explicacao") or "")
            for rotulo in (ROTULO_SUSTENTA, ROTULO_CONTRADIZ, ROTULO_NEUTRO):
                if rotulo in bruto:
                    vereditos.append((rotulo, motivo))
                    break
        return vereditos
