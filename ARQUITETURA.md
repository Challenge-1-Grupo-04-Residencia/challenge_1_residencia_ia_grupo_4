# Arquitetura do repositório

Monorepo com dois aplicativos e os dados de treino, versionados juntos porque o motor
de veracidade e a interface evoluem no mesmo ritmo e compartilham o contrato da API.

> A documentação de **produto** (requisitos, pesos dos sinais, persona, backlog) não
> está aqui: ela vive na branch [`docs`](../../tree/docs), em MkDocs Material, e é
> publicada em `gh-pages`. Os anexos formais — `Relatórios/` e
> `Referencias_bibliograficas/` — ficam lá também, ao lado das páginas que os citam.
> Este arquivo cobre só a organização do **código**.
>
> ```bash
> git show origin/docs:docs/produto/classificacao.md
> ```

## Mapa do repositório

```
├── backend/              API e motor de veracidade (Python · FastAPI)
│   ├── src/
│   │   ├── core/         domínio: não importa nada de infraestrutura
│   │   │   ├── entities/ Sinal, NoticiaRequest, AnaliseResultado
│   │   │   ├── engine/   triagem, scoring, regras, orquestrador, camadas
│   │   │   └── ports/    interfaces que a infraestrutura implementa
│   │   ├── infrastructure/
│   │   │   ├── ml_models/  classificador N2 (.joblib)
│   │   │   ├── search/     GDELT e índice TF-IDF local
│   │   │   └── sources/    base curada de veículos
│   │   └── main.py       FastAPI: monta o pipeline e traduz JSON ↔ domínio
│   ├── scripts/          diagnóstico manual (debug_pipeline.py)
│   └── tests/
├── frontend/             Site e chat (TypeScript · Next.js · Tailwind)
│   └── src/
│       ├── app/          rotas e layout (App Router)
│       ├── components/   vera/ (persona) · checagem/ (resultado) · ui/
│       ├── lib/          api.ts (único ponto de rede) · veracidade.ts
│       └── types/        espelho do contrato da API
├── scripts/              subir.sh — sobe o ambiente de desenvolvimento
├── ml/                   ciência de dados
│   ├── notebooks/        uma EDA por camada do pipeline
│   ├── scripts/          datasets, treino do S-06 e avaliação dos sinais
│   └── datasets/         corpora em Parquet (fora do controle de versão)
└── .claude/skills/       guias de trabalho por área do projeto
```

## Backend: por que a divisão core / infrastructure

A regra é uma só: **`core` não importa `infrastructure`**. O sentido inverso é livre.

Isso existe porque o motor de veracidade é a parte do produto que precisa sobreviver a
trocas de tecnologia. Ao longo do projeto vamos trocar de provedor de busca, de modelo
de ML e de LLM; nenhuma dessas trocas deveria tocar a fórmula do score ou as regras de
negócio. A dependência é invertida por uma porta:

```
CamadaN3Corroboracao  →  BuscadorDeNoticias (Protocol, em core/ports)
                              ↑ implementado por
                         BuscadorGdelt · BuscadorTfidf (em infrastructure/search)
```

É também o que permite testar as camadas sem rede: o teste passa um duplo que satisfaz
a porta.

## O fluxo de uma checagem

```
POST /api/v1/checar
      │
      ▼
            triagem: é alegação de fato, ou é "oi, tudo bem?"
                 │                            │
          não é ─┘                            └─ é ──┐
          resposta de conversa,                      │
          sem checagem e sem porcentagem             ▼
NoticiaRequest ──► N0 cache ──► N1 fonte ──► N2 conteúdo ──► N3 corroboração ──► N4 LLM
                      │            │             │                │                │
                      └────────────┴─────────────┴────────────────┴────────────────┘
                                      cada camada registra SINAIS
                                                  │
                                    regra de parada após cada camada:
                                    C ≥ 0,6 e (V ≤ 25 ou V ≥ 75) → para
                                                  │
                                                  ▼
                                    business_rules (RN-01..RN-04)
                                                  │
                                                  ▼
                                          ChecagemResponse
```

O ponto central do desenho: **camadas não calculam o score, elas produzem evidência.**
Cada camada registra sinais (`S-01` a `S-13`) com peso e dimensão vindos do catálogo, e
o score é sempre a média ponderada dos sinais **disponíveis**:

```
V = 100 × Σ(w·s) / Σ(w)
C = cobertura × concordância
```

Um sinal sem dado sai do cálculo e não vale zero (RN-06). Isso mantém separadas duas
coisas que parecem iguais no código e são opostas no produto: *não sei* derruba a
confiança, *sei que é ruim* derruba o score.

### Estado das camadas

| Camada | Status | Sinais | Responsável |
| --- | --- | --- | --- |
| Triagem | **implementada** | — (decide se há checagem) | — |
| N0 · Cache | **implementada** | S-00 (Fast-track) | — |
| N1 · Fonte | **implementada** | S-01 | — |
| N2 · Conteúdo | **implementada** | S-06, S-07, S-08, S-09 | — |
| N3 · Corroboração | **implementada** | S-11, S-13 | — |
| N4 · LLM | **implementada** | S-12 | — |

Agora que N0 e N1 estão ativas, a cobertura do catálogo abrange a dimensão de fonte (S-01 medido via histórico local de reputação). O único sinal ausente por design é S-10.

A **confiança**, porém, não é calculada sobre os 100 pontos, e sim sobre os 63 que as
camadas existentes sabem medir (`cobertura`). A razão está em
`core/engine/scoring.py`: enquanto o denominador eram os 100, o teto da confiança era
0,63, e a regra de parada — que exige `C ≥ 0,6` — nunca podia ser satisfeita antes da
N4. RN-07 virava letra morta e a LLM rodava em 100% das checagens. Sinal que a camada
*tentou* medir e não conseguiu continua derrubando a cobertura, que é o que RN-06 pede;
o que saiu da conta foi a camada que ninguém escreveu ainda.

A N4 **não carrega modelo no processo**: ela chama um LLM servido pelo Ollama por HTTP.
Quem for mexer nela precisa do serviço de pé:

```bash
docker compose up -d ollama
docker exec -it vera_ollama ollama pull llama3
```

Um sinal está fora por decisão consciente: **S-10** (texto gerado por IA) é `Won't` no
MoSCoW, porque detectores de texto por IA são pouco confiáveis e texto escrito por IA
não é falso por definição.

### Sinais que só conseguem descontar

S-07 (sensacionalismo) e S-08 (intensidade emocional) entram no cálculo em `[0; 0,5]`, e
não em `[0; 1]`, e ficam **indisponíveis** quando não encontram nada. São detectores de
manipulação: achar gritaria ou insulto é evidência contra a notícia, mas não achar não é
evidência a favor — mentira em tom sóbrio existe e é o caso difícil.

Enquanto os dois podiam valer 1,0, somavam 10 dos 23 pontos ativos quase sempre no
máximo, e o efeito medido nos corpora rotulados foi que só **11,9% a 25%** das notícias
falsas chegavam à faixa "provavelmente falsa". Depois da mudança, **96,3%**. Era também
o que dava 77% de veracidade a um "Oi, tudo bem?".

O mesmo vale para S-13: não achar cópia entre cinco resultados de busca não atesta
originalidade, então o sinal fica indisponível em vez de creditar 1,0.

## Frontend: onde mora o quê

| Camada | Responsabilidade | Não faz |
| --- | --- | --- |
| `app/` | rotas, layout, estado da conversa | regra de negócio |
| `components/checagem/` | apresentar resultado e coletar entrada | chamar a API |
| `components/vera/` | a persona e suas expressões | decidir o humor |
| `lib/api.ts` | toda a rede, erro e cancelamento | formatar para a tela |
| `lib/veracidade.ts` | faixa → cor, humor, frase | buscar dados |
| `types/checagem.ts` | contrato da API | lógica |

O frontend **não recalcula nada**. Faixa, rótulo, principais sinais e dificuldade vêm
prontos da API. Duplicar a fórmula no cliente garantiria divergência na primeira
calibração de pesos.

`types/checagem.ts` é espelho de `backend/src/main.py`: mudança de contrato altera os
dois na mesma PR.

## Rodando

```bash
./scripts/subir.sh              # backend + frontend, Ctrl+C derruba tudo
./scripts/subir.sh --com-ollama # idem, com a camada N4 ativa
./scripts/subir.sh --so-backend # só a API
```

Ou na mão:

```bash
# backend
uv sync
uv run uvicorn src.main:app --app-dir backend --reload --port 8010
uv run pytest

# frontend
export PATH="$HOME/.local/node/bin:$PATH"
cd frontend && npm install && npm run dev      # :3000
```

O `--reload` não é opcional: a auditoria de 05/10 encontrou um `uvicorn` e um
`next-server` de cinco dias antes ainda no ar, os dois sem recarregamento, servindo
código velho e dando a impressão de que o motor estava quebrado. O `subir.sh` confere as
portas e derruba o que ficou para trás antes de subir — e só derruba o que reconhece
como servidor de desenvolvimento deste projeto; qualquer outra coisa na porta faz o
script parar em vez de adivinhar.

A porta do backend é **8010** e não 8000 porque a 8000 costuma estar ocupada pelo
`mkdocs serve` da documentação. O frontend lê `NEXT_PUBLIC_API_URL` de
`frontend/.env.local` (veja `.env.example`).

Node fica em `~/.local/node/bin` — foi instalado do binário oficial porque o Homebrew
desta máquina não tem permissão de escrita em `/opt/homebrew`.

## Decisões registradas

| Decisão | Por quê |
| --- | --- |
| Monorepo, e não repositórios separados | O contrato da API muda junto com a tela; PR única evita frontend quebrado em produção |
| `pythonpath = ["backend"]` no pytest | Mantém os imports `from src....` válidos, então as branches em andamento do grupo não conflitam na merge |
| Sinais em vez de mutação direta do score | A explicação (RF-32, RF-33) precisa saber *quanto cada evidência pesou*; um score mutado perde essa informação |
| `veracidade`/`confianca` seguem graváveis | Compatibilidade com camadas ainda não migradas; o caminho correto é `registrar()` |
| Next.js no frontend | Pedido do PO. A issue #46 especificava Vite — ver a nota registrada lá |
| N4 por LLM servido via HTTP (Ollama), e não modelo no processo | O extra `nli` com torch (~2 GB) foi removido: nada importava `transformers`, e o desenho mDeBERTa não está no código |
| Triagem antes da corrente, e não como camada | Ela não mede sinal nenhum, então não teria o que registrar; e a N0 do desenho é o cache, que é issue de outra pessoa |
| Cobertura relativa ao que as camadas existentes medem | Com os 100 pontos no denominador, `C ≥ 0,6` era inalcançável e RN-07 era código morto; a lacuna do catálogo segue visível em `cobertura_do_catalogo` |
| S-07, S-08 e S-13 só descontam | Ausência de manipulação não é evidência de verdade; com teto 1,0, só 11,9% a 25% das falsas chegavam à faixa correta |
| Léxico do S-08 calibrado por *lift* nos corpora | O léxico anterior tratava "morte", "crise" e "doença" como carga emocional — palavras 2 a 4× mais frequentes em notícia **verdadeira**; a AUC do sinal era 0,39, abaixo do acaso |
| Termo político fora do léxico, mesmo com *lift* alto | RN-08: viés político é contexto e não altera o score. "comunista" (3,6) e "esquerdista" (7,7) melhorariam a métrica e violariam a regra |
| `/api/v1/checar` é `def`, não `async def` | O pipeline faz I/O bloqueante; na corrotina ele travava o event loop e duas requisições simultâneas serializavam |
| Um veredito da N4 **por evidência**, numa chamada só | Com veredito único, o sinal de peso 20 só podia valer 0,0 ou 1,0 e movia o resultado em 32 pontos sozinho |
| Falha de busca e de LLM levantam exceção própria | "ninguém publicou" e "não consegui procurar" chegavam como a mesma lista vazia, e a camada morria em silêncio |
| TF-IDF antes de embeddings na N3 | Roda offline e sem chave de API, destrava a camada agora; a porta permite trocar sem tocar no núcleo |
| Similaridade do GDELT derivada da posição | A API não expõe score de relevância; é aproximação explícita, a refinar com embeddings |
| `notebooks/`, `scripts/` e `datasets/` juntos em `ml/` | Os notebooks leem `../datasets/` e o script resolve o destino pela própria localização; mover os três juntos preserva os caminhos sem tocar em código |
| Documentação fora da `development` | Havia duas cópias divergentes; a branch `docs` é a que o workflow publica |
| `Relatórios/` e `Referencias_bibliograficas/` fora da `development` | Estavam triplicados; são anexos citados pelas páginas da branch `docs`, não artefatos de código |
| Inferência Semântica (NLI) na N4 vs Rigor Sintático | A regra de 'Sujeito/Ação idênticos' evitava alucinações ("Lula morreu" vs "Lula lamenta morte"), mas tornava a Vera incapaz de deduzir que uma notícia sobre "boato de que Lula morreu" era uma evidência *Contra* a alegação, gerando um excesso de "Inconclusivos". O prompt foi ajustado para foco semântico (Meta-Checagem). |
