# challenge_1_residencia_ia_grupo_4

Desafio 1 — **Fake News e Desinformação** · Grupo 4 · Residência em IA

**Senhora Vera** é uma assistente de checagem em formato de chat. A pessoa cola um link
ou um texto; a Vera cruza com fontes confiáveis e responde com uma porcentagem de
veracidade, os motivos e as fontes que consultou — para que quem perguntou decida com o
próprio pensamento crítico, e não apenas receba um rótulo.

Projeto conduzido pelo framework **Challenge Based Learning (CBL)**, com execução em
**Scrum adaptado** (sprints de 1 semana, dailies às segundas, quartas e sextas).

**Equipe:** Ian Costa · Luísa Brambilla · Maykon Soares · Natália Evelin · Rebeca Bontempo

## O repositório

```
backend/     API e motor de veracidade (FastAPI)    → backend/README.md
frontend/    site e chat (Next.js + Tailwind)       → frontend/README.md
datasets/    corpora brasileiros padronizados
notebooks/   análise exploratória e treino dos modelos
```

A organização do código e as decisões de arquitetura estão em
[ARQUITETURA.md](ARQUITETURA.md).

## Rodando

```bash
# backend — http://localhost:8010
uv sync                       # use `uv sync --extra nli` para habilitar a camada N4
uv run uvicorn src.main:app --app-dir backend --reload --port 8010

# frontend — http://localhost:3000
export PATH="$HOME/.local/node/bin:$PATH"
cd frontend && npm install && cp .env.example .env.local && npm run dev
```

A porta do backend é 8010 porque a 8000 costuma estar ocupada pelo `mkdocs serve` da
documentação.

```bash
uv run pytest              # testes do backend
cd frontend && npm run build   # checagem de tipos do frontend
```

## Como a Vera funciona

A checagem acontece em **camadas de custo crescente**, e para assim que há resposta —
a maioria das notícias se resolve antes de chegar na LLM.

| Camada | Pergunta | Status |
| --- | --- | --- |
| **N0** Cache | Já checei isso? | a fazer |
| **N1** Fonte | Quem publicou? | a fazer |
| **N2** Conteúdo | Como está escrito? | implementada |
| **N3** Corroboração | Outros veículos publicaram? | implementada |
| **N4** LLM | As evidências sustentam as alegações? | implementada |

Cada camada registra **sinais** (`S-01` a `S-13`) com peso próprio, e o score é a média
ponderada dos sinais disponíveis. Um sinal que não pôde ser medido sai do cálculo e não
vale zero: não saber derruba a *confiança*, não a *veracidade*.

## Análise exploratória (EDA)

O desenvolvimento dos modelos e as análises exploratórias ocorrem no branch `development`.

```bash
git switch development && git pull
uv sync
./scripts/baixar_datasets.sh    # só na primeira vez
uv run jupyter lab
```

No VS Code, abra o notebook em `notebooks/` e selecione o kernel Python de `.venv`.

## Documentação

A documentação de produto — requisitos, pesos dos sinais, persona, backlog, riscos —
vive no branch [`docs`](../../tree/docs), em MkDocs Material, e é publicada em
`gh-pages` por workflow.

```bash
git show origin/docs:docs/produto/classificacao.md     # ler um arquivo
git ls-tree -r --name-only origin/docs                 # listar
```

## Contribuindo

Branch própria → PR para `development` → PR para `main`. Nunca commite direto nessas
duas. Todo trabalho rastreia para um requisito (`RF-xx`), e a
[Definition of Done](../../tree/docs/docs/backlog/dor-dod.md) exige teste, revisão de um
colega e documentação atualizada com linha nova no histórico de revisão da página.

Há skills em `.claude/skills/` com o passo a passo de cada área: `vera-sinais`,
`vera-camadas`, `vera-backlog` e `vera-frontend`.
