# Backend — API e motor de veracidade

FastAPI + Python 3.14. O motor decide a veracidade de uma notícia coletando **sinais**
em camadas de custo crescente e parando assim que tem resposta.

```bash
uv sync
uv run uvicorn src.main:app --app-dir backend --reload --port 8010
uv run pytest
```

Porta 8010 porque a 8000 costuma estar ocupada pelo `mkdocs serve` da documentação.
Docs interativas em <http://localhost:8010/docs>.

## Endpoints

| Método | Rota | O que faz |
| --- | --- | --- |
| `POST` | `/api/v1/checar` | Checa um texto, link ou afirmação |
| `GET` | `/health` | Verificação de disponibilidade |

### `POST /api/v1/checar`

```json
{ "texto": "URGENTE!!! REPASSEM!!! ...", "url": null }
```

```json
{
  "veracidade": 8.51,
  "confianca": 0.18,
  "faixa": "Inconclusiva",
  "camada_parada": "N3",
  "dificuldade": "mediano",
  "explicacao": "Não encontrei evidências suficientes para cravar um resultado. ...",
  "exibe_porcentagem": false,
  "regra_aplicada": "RN-04",
  "cobertura": 0.18,
  "principais_sinais": [ { "id": "S-06", "peso": 10, "score": 0.02, "...": "..." } ],
  "sinais": [ { "id": "S-11", "peso": 15, "score": null, "...": "..." } ],
  "documentos_relacionados": [],
  "fontes_citadas": []
}
```

Três campos que costumam ser mal usados por quem consome:

- **`veracidade` pode ser `null`** — opinião e sátira não recebem porcentagem (RN-03).
  Verifique `exibe_porcentagem` antes de renderizar o número.
- **`score` de um sinal pode ser `null`** — significa que o sinal não pôde ser medido e
  **saiu do cálculo** (RN-06). Não o trate como zero.
- **`regra_aplicada`** explica por que o resultado publicado difere da média ponderada
  dos sinais. Se vier preenchido, mostre o motivo junto ao número.

## Estrutura

```
src/
├── core/                 domínio — não importa nada de infrastructure
│   ├── entities/
│   │   ├── signal.py     catálogo S-01..S-13 com pesos e dimensões
│   │   └── claim.py      NoticiaRequest, AnaliseResultado, DocumentoRelacionado
│   ├── engine/
│   │   ├── scoring.py    fórmulas de V e C, faixas, regra de parada
│   │   ├── business_rules.py   RN-01..RN-04
│   │   ├── orchestrator.py     Chain of Responsibility
│   │   ├── n2_content.py       camada N2
│   │   ├── n3_corroboration.py camada N3
│   │   ├── n4_nli.py           camada N4 (inferência NLI)
│   │   └── text_style.py       heurísticas de sensacionalismo e citação
│   └── ports/            interfaces (Protocol) para a infraestrutura
├── infrastructure/
│   ├── ml_models/        classificador N2 treinado (.joblib)
│   ├── search/           BuscadorGdelt · BuscadorTfidf
│   └── sources/          base curada de veículos
└── main.py               monta o pipeline, traduz JSON ↔ domínio
```

## O cálculo

```
V = 100 × Σ(w·s) / Σ(w)      sobre os sinais DISPONÍVEIS
C = cobertura × concordância
    cobertura    = Σ(w disponível) / 100
    concordância = 1 − σ(scores por dimensão)
```

Camadas **não calculam o score** — registram sinais, e o score é recalculado a cada
registro. Os pesos vêm de `origin/docs:docs/produto/classificacao.md` e são hipótese de
partida: a calibração com dataset rotulado (RNF-07) deve mudá-los, registrando a mudança
no histórico daquela página.

## Estado das camadas

N2, N3 e N4 estão implementadas; N0 e N1 são issues em aberto de outras pessoas do grupo.
Com isso a cobertura máxima é de 53 pontos — a dimensão Fonte inteira (35) fica de fora,
mais S-08 e S-10. Muita checagem ainda cai em RN-04 (Inconclusivo). **É o comportamento
correto**: a Vera não crava veredito sem evidência.

A N4 precisa do extra opcional do NLI, que traz o torch (~2 GB):

```bash
uv sync --extra nli
```

Para adicionar uma camada ou um sinal, veja as skills `vera-camadas` e `vera-sinais` em
`.claude/skills/`.

## Testes

```bash
uv run pytest                                  # tudo
uv run pytest backend/tests/test_scoring.py    # só as fórmulas
```

`test_scoring.py` inclui `test_exemplo_da_documentacao`, que reproduz o exemplo numérico
de `classificacao.md`. Ele quebra de propósito se alguém mudar peso sem atualizar a
documentação.

Nenhum teste toca a rede: as dependências externas entram por porta e são substituídas
por duplos.
