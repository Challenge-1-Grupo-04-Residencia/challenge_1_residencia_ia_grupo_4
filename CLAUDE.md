# Senhora Vera — contexto do projeto

Checador de notícias em formato de chat. Grupo 4 da Residência em IA, Challenge 1 (Fake
News e Desinformação), conduzido por Challenge Based Learning com Scrum adaptado.

## Onde está o quê

- **Código**: branch `development` (é de onde saem as branches de feature)
- **Documentação de produto**: branch **`docs`**, em MkDocs — requisitos, pesos dos
  sinais, persona, backlog. Leia com `git show origin/docs:<caminho>`
- **Site publicado**: branch `gh-pages`, gerada por workflow (não editar à mão)
- **Organização do código**: [ARQUITETURA.md](ARQUITETURA.md)

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
  externas (nunca rede em teste)

## Comandos

```bash
uv sync                                                        # ambiente Python
uv run pytest                                                  # testes do backend
uv run uvicorn src.main:app --app-dir backend --reload --port 8010

export PATH="$HOME/.local/node/bin:$PATH"                      # Node não está no brew
cd frontend && npm run dev                                     # :3000
cd frontend && npm run build                                   # checa tipos de verdade
```

Backend na **8010**: a 8000 costuma estar ocupada pelo `mkdocs serve`. No frontend,
`npx tsc --noEmit` falha com `Cannot find name 'LayoutProps'` — é esperado, o Next gera
esse tipo no build; use `npm run build`.

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
