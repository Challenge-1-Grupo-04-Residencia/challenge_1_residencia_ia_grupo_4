---
name: vera-camadas
description: Use ao implementar ou alterar uma camada do pipeline da Vera (N0 cache, N1 fonte, N2 conteúdo, N3 corroboração, N4 LLM), ao integrar uma API externa de checagem, ou ao mexer no orquestrador. Gatilhos: "camada N0".."camada N4", "orquestrador", "chain of responsibility", "GDELT", "Fact Check API", "RDAP", "WHOIS", "NLI", "reputação de domínio", "busca de notícias semelhantes", "pipeline em camadas".
---

# Camadas do pipeline da Vera

A Vera checa em camadas que vão da mais barata para a mais cara, e **para assim que
tem resposta**. É isso que torna o produto viável: a maioria das notícias se resolve
antes de chegar na LLM.

| Camada | Pergunta | Técnica | Latência alvo |
| --- | --- | --- | --- |
| **N0** Cache | Já checei isso? | Hash de URL, similaridade | < 200 ms |
| **N1** Fonte | Quem publicou? | Base curada, RDAP, Fact Check API | < 2 s |
| **N2** Conteúdo | Como está escrito? | TF-IDF + SVM, heurísticas, léxico | < 1 s |
| **N3** Corroboração | Outros publicaram? | GDELT, busca, embeddings | < 8 s |
| **N4** LLM | As evidências sustentam? | LLM + NLI | < 20 s |

Estado atual: **N2, N3 e N4 implementadas**. N0 e N1 são issues de outras pessoas do
grupo — não as implemente sem combinar antes.

A N4 exige `uv sync --extra nli` (traz o torch, ~2 GB). Sem o extra ela falha com
mensagem explícita; os testes injetam um classificador falso e não baixam o modelo.

## Como se escreve uma camada

```python
class CamadaN1Fonte(CamadaVerificacao):
    """Camada N1 · Fonte — avalia quem publicou (RF-14 a RF-19)."""

    def __init__(self, consulta_dominio: ConsultaDeDominio):
        super().__init__()
        self.consulta_dominio = consulta_dominio  # injetado, nunca instanciado aqui

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        resultado = noticia.resultado
        resultado.camada_atual = "N1"

        # mede o que sabe medir e registra como sinal
        resultado.registrar(medir("S-03", idade_normalizada, "Domínio com 20 dias."))

        return self.repassar(noticia)   # SEMPRE termina assim
```

Quatro regras que valem para toda camada:

1. **Marque `camada_atual`** na entrada. É o que define a dificuldade da checagem (RF-13).
2. **Expresse tudo como sinal**, via `resultado.registrar(...)`. Nunca mexa em
   `veracidade` ou `confianca` direto — o valor gravado à mão não entra na explicação
   nem na cobertura, e desaparece do detalhamento que RF-33 exige.
3. **Termine com `self.repassar(noticia)`.** É o `repassar` que consulta a regra de
   parada; um `return noticia` seco quebra o encadeamento silenciosamente.
4. **Receba dependências externas por injeção**, tipadas por uma porta em
   `src/core/ports/`. O núcleo não importa `httpx` nem cliente de API.

## Falha de rede não é evidência de falsidade

Este é o erro mais fácil de cometer numa camada que chama API externa. Se a Fact Check
API cai, o resultado correto é o sinal **indisponível** (RN-06), não score zero.

Implementações de porta devolvem vazio em vez de levantar exceção — veja o `except` em
`backend/src/infrastructure/search/gdelt.py`. A camada traduz vazio em `medir(..., None,
"a busca não devolveu resultados")`.

## Regra de parada

Em `scoring.deve_parar`: para se `C ≥ 0,7` **e** (`V ≤ 25` ou `V ≥ 75`).

A segunda condição é o detalhe que se esquece: com `V = 50` e confiança altíssima a Vera
**continua subindo camadas**, porque um resultado ambíguo com confiança alta ainda não
responde à pergunta de quem perguntou. Por RN-07 a N4 só roda se N0–N3 não bastaram.

## Montar o pipeline

O encadeamento vive em `obter_orquestrador()`, em `backend/src/main.py`, sob
`lru_cache`: o classificador da N2 e os índices de busca são caros de carregar e não
podem ser reconstruídos por requisição.

```python
n2.set_proxima(n3)            # set_proxima devolve a camada, então dá para encadear
orquestrador = Orquestrador(n2)
veredito = orquestrador.veredito(noticia)   # roda e aplica RN-01..RN-04
```

Use `.veredito()` e não `.checar()` quando quiser o resultado publicável: `checar` roda
o pipeline mas não aplica as regras de negócio.

## Testar uma camada

Sempre com um duplo da dependência externa, nunca com rede — veja `BuscadorFalso` em
`backend/tests/test_n3_corroboration.py`. Casos que todo teste de camada deve cobrir:

- o sinal é medido corretamente no caminho felizo
- dependência indisponível → sinal `None`, não `0.0`
- a camada repassa adiante quando a regra de parada não foi atingida
- `camada_atual` foi marcada

```bash
uv run pytest backend/tests/ -q
uv run uvicorn src.main:app --app-dir backend --reload --port 8010
```

Use 8010 e não 8000: a 8000 costuma estar ocupada pelo `mkdocs serve` do projeto.
