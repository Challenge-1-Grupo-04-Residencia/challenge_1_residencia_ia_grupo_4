# challenge_1_residencia_ia_grupo_4

Desafio 1 — **Fake News e Desinformação** · Grupo 4 · Residência em IA

Projeto conduzido pelo framework **Challenge Based Learning (CBL)**, com execução em
**Scrum adaptado** (sprints de 1 semana, dailies às segundas, quartas e sextas).

**Equipe:** Ian Costa · Luísa Brambilla · Maykon Soares · Natália Evelin · Rebeca Bontempo

## Documentação

A documentação do projeto vive no branch [`docs`](../../tree/docs), em MkDocs Material.

```bash
git checkout docs
uv sync
uv run mkdocs serve   # http://127.0.0.1:8000
```

A cada push no branch `docs`, a Action [`deploy-docs.yml`](.github/workflows/deploy-docs.yml)
publica o site no GitHub Pages (branch `gh-pages`).

- **Página inicial:** template em [`overrides/home.html`](overrides/home.html), no mesmo estilo
  do projeto Paraizo. Cores em [`overrides/stylesheets/extra.css`](overrides/stylesheets/extra.css).
- **Membros da seção "Nosso Time":** preencha `extra.equipe` no [`mkdocs.yml`](mkdocs.yml)
  (nome, papel, foto em `docs/assets/equipe/` e usuário do GitHub).
- **Histórico de revisão:** toda página tem uma tabela recolhível no topo; adicione uma linha
  a cada alteração.

| Página | Conteúdo |
| --- | --- |
| `docs/desafio.md` | Big Idea, Essential Question, Challenge e Guiding Questions |
| `docs/metodologia.md` | Scrum adaptado: sprints, cerimônias, artefatos, papéis |
| `docs/hipoteses.md` | Ideações preliminares (a validar na fase Investigate) |
| `docs/relatorios.md` | Entregas formais por fase |
| `docs/referencias.md` | Bibliografia e ferramentas citadas |

## Estrutura

```
Relatorios/                  entregas formais (PDF)
Referencias_bibliograficas/  bibliografia (PDF)
docs/                        fonte da documentação MkDocs
mkdocs.yml                   configuração do site
```

## Status

- [x] Semana 1 — **Engage**
- [ ] Semanas 2 e 3 — **Investigate**
- [ ] Semanas 4 e 5 — **Act**
