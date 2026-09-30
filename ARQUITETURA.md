# Arquitetura do repositório

Monorepo com dois aplicativos e os dados de treino, versionados juntos porque o motor
de veracidade e a interface evoluem no mesmo ritmo e compartilham o contrato da API.

> A documentação de **produto** (requisitos, pesos dos sinais, persona, backlog) não
> está aqui: ela vive na branch [`docs`](../../tree/docs), em MkDocs Material, e é
> publicada em `gh-pages`. Este arquivo cobre só a organização do **código**.
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
│   │   │   ├── engine/   scoring, regras de negócio, orquestrador, camadas
│   │   │   └── ports/    interfaces que a infraestrutura implementa
│   │   ├── infrastructure/
│   │   │   ├── ml_models/  classificador N2 (.joblib)
│   │   │   ├── search/     GDELT e índice TF-IDF local
│   │   │   └── sources/    base curada de veículos
│   │   └── main.py       FastAPI: monta o pipeline e traduz JSON ↔ domínio
│   └── tests/
├── frontend/             Site e chat (TypeScript · Next.js · Tailwind)
│   └── src/
│       ├── app/          rotas e layout (App Router)
│       ├── components/   vera/ (persona) · checagem/ (resultado) · ui/
│       ├── lib/          api.ts (único ponto de rede) · veracidade.ts
│       └── types/        espelho do contrato da API
├── ml/                   ciência de dados
│   ├── notebooks/        uma EDA por camada do pipeline
│   ├── scripts/          download e padronização dos datasets
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
NoticiaRequest ──► N0 cache ──► N1 fonte ──► N2 conteúdo ──► N3 corroboração ──► N4 LLM
                      │            │             │                │                │
                      └────────────┴─────────────┴────────────────┴────────────────┘
                                      cada camada registra SINAIS
                                                  │
                                    regra de parada após cada camada:
                                    C ≥ 0,7 e (V ≤ 25 ou V ≥ 75) → para
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
| N0 · Cache | a fazer | — | issue em aberto |
| N1 · Fonte | a fazer | S-01 a S-05 | issue em aberto |
| N2 · Conteúdo | **implementada** | S-06, S-07, S-09 | — |
| N3 · Corroboração | **implementada** | S-11, S-13 | — |
| N4 · LLM | **implementada** | S-12 | — |

Com N0 e N1 pendentes a cobertura máxima é de 53 dos 100 pontos: os 35 da dimensão
Fonte inteira ficam de fora, mais S-08 e S-10. Por isso muita checagem ainda cai em
RN-04 (Inconclusivo) por confiança baixa. **Isso é o comportamento correto**, não um
bug: a Vera não deve cravar veredito sem evidência. O número sobe conforme as camadas
entram.

A N4 exige o extra opcional do NLI, que traz o torch (~2 GB):

```bash
uv sync --extra nli
```

Dois sinais estão fora por decisão consciente: **S-08** (intensidade emocional) espera a
integração do NRC Emotion Lexicon, e **S-10** (texto gerado por IA) é `Won't` no MoSCoW,
porque detectores de texto por IA são pouco confiáveis e texto escrito por IA não é
falso por definição.

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
# backend
uv sync
uv run uvicorn src.main:app --app-dir backend --reload --port 8010
uv run pytest

# frontend
export PATH="$HOME/.local/node/bin:$PATH"
cd frontend && npm install && npm run dev      # :3000
```

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
| `transformers` como extra opcional `nli` | Traz o torch (~2 GB) e só a N4 usa; pesaria no `uv sync` de quem só mexe nos notebooks |
| TF-IDF antes de embeddings na N3 | Roda offline e sem chave de API, destrava a camada agora; a porta permite trocar sem tocar no núcleo |
| Similaridade do GDELT derivada da posição | A API não expõe score de relevância; é aproximação explícita, a refinar com embeddings |
| `notebooks/`, `scripts/` e `datasets/` juntos em `ml/` | Os notebooks leem `../datasets/` e o script resolve o destino pela própria localização; mover os três juntos preserva os caminhos sem tocar em código |
| Documentação fora da `development` | Havia duas cópias divergentes; a branch `docs` é a que o workflow publica |
