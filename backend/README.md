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
| `POST` | `/api/v1/perguntar` | Pergunta de acompanhamento sobre um resultado (RF-04) |
| `GET` | `/api/v1/checagens/recentes` | Feed das últimas checagens (RF-43) |
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
  "cobertura": 0.29,
  "cobertura_do_catalogo": 0.18,
  "principais_sinais": [ { "id": "S-06", "peso": 10, "score": 0.02, "...": "..." } ],
  "sinais": [ { "id": "S-11", "peso": 15, "score": null, "...": "..." } ],
  "documentos_relacionados": [],
  "fontes_citadas": []
}
```

Campos que costumam ser mal usados por quem consome:

- **`veracidade` pode ser `null`** — opinião e sátira não recebem porcentagem (RN-03), e
  entrada que não é alegação de fato também não. Verifique `exibe_porcentagem` antes de
  renderizar o número.
- **`score` de um sinal pode ser `null`** — significa que o sinal não pôde ser medido e
  **saiu do cálculo** (RN-06). Não o trate como zero.
- **`regra_aplicada`** explica por que o resultado publicado difere da média ponderada
  dos sinais. Se vier preenchido, mostre o motivo junto ao número.
- **`faixa` pode ser `"Conversa"`**, com `camada_parada: "TRIAGEM"` — a entrada era
  saudação ou conversa e não houve checagem. Não é o mesmo que `"Inconclusiva"`, que é
  um resultado de checagem. Nesse caso só a `explicacao` tem conteúdo útil: não mostre
  confiança, cobertura nem dificuldade.
- **`cobertura` e `cobertura_do_catalogo` são coisas diferentes.** A primeira é a fração
  do que as camadas existentes sabem medir e alimenta a confiança; a segunda é a fração
  dos 100 pontos do catálogo e mede a maturidade do produto. Para o usuário, mostre a
  primeira.

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
│   │   ├── triagem.py          é alegação de fato, ou é conversa?
│   │   ├── n2_content.py       camada N2
│   │   ├── n3_corroboration.py camada N3
│   │   ├── n4_nli.py           camada N4 (LLM via Ollama)
│   │   ├── emotion.py          léxico de carga emocional (S-08)
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
    cobertura    = Σ(w disponível) / Σ(w MENSURÁVEL)
    concordância = 1 − σ(scores por dimensão)
```

O denominador da cobertura é o peso que as camadas existentes **sabem medir** (63 hoje),
e não os 100 do catálogo. Com os 100 ali, o teto da confiança era 0,63 enquanto N0 e N1
não existissem, e a regra de parada — que exige `C ≥ 0,6` — nunca podia ser satisfeita
antes da N4: RN-07 era código morto e a LLM rodava em toda checagem. Sinal que a camada
*tentou* medir e não conseguiu continua derrubando a cobertura, que é o que RN-06 pede.

S-07, S-08 e S-13 vivem em `[0; 0,5]` e ficam indisponíveis quando não acham nada: são
detectores de manipulação, e não achar manipulação não é evidência de verdade.

Camadas **não calculam o score** — registram sinais, e o score é recalculado a cada
registro. Os pesos vêm de `origin/docs:docs/produto/classificacao.md` e são hipótese de
partida: a calibração com dataset rotulado (RNF-07) deve mudá-los, registrando a mudança
no histórico daquela página.

## Estado das camadas

A triagem, a N2, a N3 e a N4 estão implementadas; N0 e N1 são issues em aberto de outras
pessoas do grupo. Com isso 37 dos 100 pontos do catálogo ficam fora — a dimensão Fonte
inteira (35) e S-10 —, o que aparece em `cobertura_do_catalogo`.

A N4 **não carrega modelo no processo**: ela chama um LLM servido pelo Ollama por HTTP.
Sem o serviço de pé, S-12 fica indisponível e a explicação diz que a conferência não foi
possível — comportamento correto, não erro a esconder.

```bash
docker compose up -d ollama
docker exec -it vera_ollama ollama pull llama3
```

O GDELT, fonte da N3, responde em 15 a 25 s no plano gratuito e aceita uma consulta a
cada 5 s. O adaptador foi ajustado para isso (timeout, espaçamento, log), mas **a fonte
não fecha o orçamento de latência da camada** — a decisão de trocar de provedor ou montar
índice próprio está aberta e é do PO.

Para adicionar uma camada ou um sinal, veja as skills `vera-camadas` e `vera-sinais` em
`.claude/skills/`.

## Testes

```bash
uv run pytest                                  # tudo
uv run pytest backend/tests/test_scoring.py    # só as fórmulas
```

Eficácia dos sinais contra os corpora rotulados — rode sempre que mexer em peso, léxico
ou limiar, e atualize a linha de base no mesmo commit:

```bash
uv run python ml/scripts/avaliar_sinais.py
uv run python ml/scripts/treinar_classificador_n2.py   # retreina o S-06
uv run python backend/scripts/debug_pipeline.py "o texto"
uv run python backend/scripts/bateria_de_exemplos.py
```

A bateria roda o pipeline em 25 exemplos com gabarito — as alegações falsas são reais,
colhidas dos títulos das checagens publicadas pelo G1 Fato ou Fake e pelo Aos Fatos.
Erro para o lado de "Inconclusiva" é aceitável e está contado em separado: por RN-04 e
RN-12 a Vera deve se recusar a cravar quando não apurou. Veredito **trocado** é bug de
produto, e aí o script sai com código 1.

Teste que dá `skip` quando um serviço está desligado não é cobertura. Os casos que
exigem o Ollama de verdade ficam em `tests/laboratorio_n4.py`, que é script e não suíte:

```bash
uv run python backend/tests/laboratorio_n4.py
```

`test_scoring.py` inclui `test_exemplo_da_documentacao`, que reproduz o exemplo numérico
de `classificacao.md`. Ele quebra de propósito se alguém mudar peso sem atualizar a
documentação.

Nenhum teste toca a rede: as dependências externas entram por porta e são substituídas
por duplos.
