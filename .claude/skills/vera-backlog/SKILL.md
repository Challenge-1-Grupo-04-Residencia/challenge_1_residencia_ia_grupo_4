---
name: vera-backlog
description: Use ao trabalhar numa issue do projeto, abrir branch ou PR, escrever mensagem de commit, ou checar DoR/DoD. Também para localizar a documentação do projeto (que vive na branch docs, não na development). Gatilhos: "issue", "pull request", "PR", "branch", "commit", "DoR", "DoD", "definition of done", "RF-", "épico", "sprint", "onde está a documentação", "mkdocs".
---

# Fluxo de trabalho do Grupo 4

## A documentação NÃO está na branch de código

Isto é a primeira coisa a saber, e a que mais custa tempo quando se ignora. A `development`
tem código e datasets; a documentação MkDocs vive na branch **`docs`**, e a `gh-pages` é
só o build publicado dela.

```bash
git show origin/docs:docs/produto/classificacao.md    # ler um arquivo
git ls-tree -r --name-only origin/docs                # listar o que existe
```

Nunca edite `gh-pages` à mão: ela é gerada pelo workflow `.github/workflows/deploy-docs.yml`.

### O que tem lá

| Arquivo | Conteúdo |
| --- | --- |
| `docs/produto/classificacao.md` | Sinais, pesos, fórmulas, faixas, histórico de calibração |
| `docs/produto/funcionamento.md` | Pipeline em camadas, regra de parada, latências |
| `docs/produto/vera.md` | Persona, canais, frases temáticas, identidade visual |
| `docs/requisitos/funcionais.md` | RF-01 a RF-43 |
| `docs/requisitos/regras-de-negocio.md` | RN-01 a RN-12 |
| `docs/backlog/dor-dod.md` | Definition of Ready e of Done |

Todo trabalho de código rastreia para um RF. Se não rastreia, falta requisito — abra a
conversa antes de codar.

## Branch e PR

Fluxo obrigatório: **branch própria → PR para `development` → PR de `development` para `main`.**
Nunca commite direto em `development` nem em `main`.

```bash
git switch development && git pull
git switch -c feat/us-score-veracidade      # feat/ · fix/ · docs/ · chore/
# ... trabalho ...
gh pr create --base development --fill
```

Nomes de branch seguem o que já existe no repositório: `feat/us-<slug-da-historia>`
para história de usuário, `feat/<slug>` para task.

Commits em português, no imperativo, com escopo entre parênteses quando ajudar:

```
feat(N3): implementa busca de notícias semelhantes por similaridade
fix(scoring): sinal indisponível deixa de contar como zero
docs(classificacao): registra calibração dos pesos da dimensão Fonte
```

Sempre cite a issue no corpo do PR (`Closes #32`), porque é o que liga o código ao RF e
ao épico.

## Definition of Ready

Uma issue só entra em sprint com: ID de RF/RNF próprio, canal e persona, forma objetiva
de verificação, épico ligado, estimativa em story points, valor de negócio do PO, caber
em uma semana, dependências disponíveis, riscos mapeados e nenhuma dúvida aberta.

## Definition of Done

Antes de pedir review, confira os sete itens:

- [ ] Comportamento do requisito implementado e demonstrável
- [ ] Código em PR, aprovado por **pelo menos um colega**
- [ ] Testes cobrem o comportamento descrito no requisito
- [ ] RNFs e RNs aplicáveis respeitados
- [ ] **A resposta da Vera explica os critérios usados** — o usuário entende por que
      aquela veracidade. Esta é a que mais se esquece, e é a alma do produto: a Vera
      existe para fortalecer o pensamento crítico, não para dar um rótulo
- [ ] Documentação afetada atualizada na branch `docs`, **com linha nova no histórico
      de revisão da página**
- [ ] Apresentada na Sprint Review e aceita pelo PO

## Equipe

Maykon Soares (PO, dev) · Ian Costa (Scrum Master, dev) · Luísa Brambilla · Natália
Evelin · Rebeca Bontempo.

Antes de mexer em camada que não é sua, confira de quem é a issue — o pipeline tem cinco
camadas divididas entre cinco pessoas, e refatorar a camada de outro sem avisar gera
conflito de merge.

```bash
gh issue list --assignee "@me" --state open
gh issue view <n>
```
