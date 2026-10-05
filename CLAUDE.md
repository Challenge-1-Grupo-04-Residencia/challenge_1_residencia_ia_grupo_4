# Senhora Vera — contexto do projeto

Checador de notícias em formato de chat. Grupo 4 da Residência em IA, Challenge 1 (Fake
News e Desinformação), conduzido por Challenge Based Learning com Scrum adaptado.

## Onde está o quê

- **Código**: branch `development` (é de onde saem as branches de feature)
- **Documentação de produto**: branch **`docs`**, em MkDocs — requisitos, pesos dos
  sinais, persona, backlog. Leia com `git show origin/docs:<caminho>`
- **Site publicado**: branch `gh-pages`, gerada por workflow (não editar à mão)
- **Organização do código**: [ARQUITETURA.md](ARQUITETURA.md)

```
backend/   API e motor de veracidade (FastAPI)
frontend/  site e chat (Next.js)
ml/        notebooks, scripts de dados e datasets
```

Os três diretórios de `ml/` andam juntos: os notebooks leem `../datasets/` e o script
resolve o destino pela própria localização.

## O que este produto é

A Vera não responde "fake ou não fake". Ela mostra o caminho: quais fontes consultou,
que sinais encontrou e **quanto cada um pesou**, para que o usuário decida com o próprio
pensamento crítico. A explicabilidade não é um extra da interface — é o produto. Um
resultado sem explicação não é exibido (RN-05).

## Regras que atravessam todo o código

Quebrar qualquer uma destas é bug de produto, não questão de estilo:

- **RN-06** — sinal sem dado é excluído do cálculo e **nunca vale zero**. "Não consegui
  medir" e "medi e está ruim" são opostos; confundi-los faz a Vera acusar de falsidade
  toda notícia sobre a qual não sabe nada. Falha de rede ou API fora também caem aqui.
  O contrário vale igual: **ausência de sinal ruim não é evidência de verdade**. S-07,
  S-08 e S-13 só conseguem descontar, e ficam indisponíveis quando não acham nada — foi
  o conserto que tirou uma saudação de 77% de veracidade.
- **RN-03** — opinião e sátira não recebem porcentagem de veracidade.
- **RN-07** — a LLM (N4) só é chamada se N0 a N3 não bastaram. É o que torna o produto
  viável economicamente.
- **RN-11** — o humor da persona acompanha o resultado técnico, nunca o substitui.
- **RN-12** — a Vera não afirma certeza absoluta: "provavelmente", "confirmada **por
  fontes**".

A lista completa (RN-01 a RN-12) está em `origin/docs:docs/requisitos/regras-de-negocio.md`.

## Convenções

- Código, comentários, commits e docstrings em **português**
- Todo trabalho rastreia para um **RF-xx**; sem requisito, converse antes de codar
- Branch própria → PR para `development` → PR para `main`. Nunca commite direto
- Commits no imperativo: `feat(N3): implementa busca por similaridade`
- Testes para o comportamento descrito no requisito, com duplo das dependências
  externas (nunca rede em teste). Teste que dá `skip` quando um serviço está desligado
  não é cobertura: é cobertura zero disfarçada. Script de laboratório que bate na rede
  mora fora da suíte (`backend/tests/laboratorio_n4.py`)
- Mexeu em peso, léxico ou limiar? Rode `ml/scripts/avaliar_sinais.py` e atualize a
  linha de base no mesmo commit. Calibragem sem medição foi como S-07 e S-08 passaram
  meses com AUC abaixo do acaso

## Comandos

```bash
./scripts/subir.sh                                             # sobe backend + frontend
./scripts/subir.sh --com-ollama                                # idem, com a N4 ativa

uv sync                                                        # ambiente Python
uv run pytest                                                  # testes do backend
uv run uvicorn src.main:app --app-dir backend --reload --port 8010

export PATH="$HOME/.local/node/bin:$PATH"                      # Node não está no brew
cd frontend && npm run dev                                     # :3000
cd frontend && npm run build                                   # checa tipos de verdade

./ml/scripts/baixar_datasets.sh                                # datasets (1ª vez)
uv run jupyter lab                                             # notebooks em ml/

uv run python ml/scripts/avaliar_sinais.py                     # eficácia dos sinais
uv run python ml/scripts/treinar_classificador_n2.py           # retreina o S-06
uv run python backend/scripts/debug_pipeline.py "texto"        # pipeline no terminal
uv run python backend/scripts/bateria_de_exemplos.py           # 25 casos com gabarito
```

A camada N4 **não carrega modelo**: ela chama um LLM pelo Ollama em HTTP. Para exercitá-la
de verdade, `docker compose up -d ollama` e `docker exec -it vera_ollama ollama pull
llama3`. Sem o serviço de pé, S-12 sai indisponível — o que é o comportamento correto, e
não um erro a esconder.

Backend na **8010**: a 8000 costuma estar ocupada pelo `mkdocs serve`. **Sempre com
`--reload`**: já aconteceu de um servidor sem reload ficar dias no ar servindo código
velho e dar a impressão de que o motor estava quebrado. No frontend, `npx tsc --noEmit`
falha com `Cannot find name 'LayoutProps'` — é esperado, o Next gera esse tipo no build;
use `npm run build`.

## Skills disponíveis

| Skill | Quando |
| --- | --- |
| `vera-sinais` | criar/calibrar sinal, fórmulas de score, regras RN-xx |
| `vera-camadas` | implementar camada N0–N4, integrar API externa, orquestrador |
| `vera-backlog` | issues, branches, PRs, DoR/DoD, achar a documentação |
| `vera-frontend` | componentes, persona, exibição de resultado |

## Equipe

Maykon Soares (PO, dev) · Ian Costa (Scrum Master, dev) · Luísa Brambilla · Natália
Evelin · Rebeca Bontempo.

As cinco camadas do pipeline estão divididas entre as cinco pessoas. Antes de mexer em
camada que não é sua, confira de quem é a issue — refatorar a camada de outro sem avisar
gera conflito de merge.
