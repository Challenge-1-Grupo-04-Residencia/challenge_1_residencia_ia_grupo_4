---
name: vera-frontend
description: Use ao mexer no frontend web da Vera — componentes React, Next.js, Tailwind, a persona e suas reações, exibição de resultado de checagem, ou o cliente da API. Gatilhos: "frontend", "componente", "Next", "React", "Tailwind", "chat da Vera", "avatar", "persona", "humor da Vera", "faixa de veracidade na tela", "exibir resultado", "PWA", "extensão".
---

# Frontend da Vera

Next.js 15 (App Router) + TypeScript + Tailwind v4, em `frontend/`.

```bash
export PATH="$HOME/.local/node/bin:$PATH"   # o Node está aqui, não no Homebrew
cd frontend && npm run dev                  # :3000
npm run build                               # valida os tipos de verdade
```

`npx tsc --noEmit` **falha** com `Cannot find name 'LayoutProps'` e isso é esperado: o
Next gera esse tipo durante o build. Use `npm run build` para checar tipos.

## Arquitetura

```
src/
  app/          rotas e layout (App Router)
  components/
    vera/       a persona: avatar e suas expressões
    checagem/   entrada, etapas, resultado, detalhamento
    ui/         primitivos reutilizáveis
  lib/
    api.ts      ÚNICO lugar que fala com o backend
    veracidade.ts  faixas → cor, humor e frase
  types/
    checagem.ts espelho do contrato da API
```

Duas fronteiras que não se atravessam:

- **Componentes não chamam `fetch`.** Importam de `lib/api.ts`, onde ficam URL base,
  tratamento de erro e cancelamento. Um `fetch` solto num componente é o começo de
  cinco tratamentos de erro diferentes.
- **`types/checagem.ts` espelha `backend/src/main.py`.** Mudou o contrato no backend,
  mude aqui na mesma PR, ou o erro vira `undefined` em tempo de execução.

## As regras de produto que o frontend precisa respeitar

Estas não são preferências de design — são regras de negócio, e quebrar qualquer uma
delas é bug de produto.

- **RN-05** — todo resultado mostra porcentagem, rótulo da faixa, principais sinais e
  fontes. *Resultado sem explicação não é exibido.*
- **RN-03** — opinião e sátira **não recebem porcentagem**. Respeite
  `exibe_porcentagem`; não caia no `veracidade ?? 50`.
- **RN-11** — a frase da Vera aparece **junto** com o dado técnico, nunca no lugar dele.
  Se o humor da persona substituir o número, a Vera deixou de ser ferramenta de
  pensamento crítico e virou entretenimento.
- **RN-12** — nunca escreva "verdadeira" seco. Os rótulos usam "provavelmente" e
  "confirmada **por fontes**", e vêm da API: não reescreva no frontend.
- **RF-33** — o detalhamento mostra **também os sinais indisponíveis**. Esconder o que
  a Vera não conseguiu medir faz a checagem parecer mais completa do que foi.

## Persona

`estiloDaFaixa(faixa)` em `lib/veracidade.ts` mapeia faixa → humor, cor e frase. Para
mudar a reação da Vera, mexa **nessa tabela**, não nos componentes — os humores também
alimentam o `VeraAvatar`, e duplicar o mapeamento faz avatar e cor divergirem.

O avatar é SVG inline, não imagem: a extensão de navegador e o PWA precisam de algo
leve, e trocar de expressão passa a ser mudança de atributo em vez de download.

Frases e identidade visual estão em `docs/produto/vera.md`, na branch `docs`:
`git show origin/docs:docs/produto/vera.md`.

## Acessibilidade e responsividade

São RNFs, não extras. O site atende **a partir de 360 px** (RNF-10), e grande parte da
desinformação circula por mensageiro no celular — o celular é o caso principal, não o
caso de borda.

- estados de carregamento com `role="status"` e `aria-live="polite"`
- a barra de veracidade é `role="meter"` com `aria-valuenow`
- o avatar tem `role="img"` e `aria-label` descrevendo a expressão
- cor nunca é o único portador de informação: a faixa vem sempre escrita também

## Variável de ambiente

`NEXT_PUBLIC_API_URL` aponta para o backend (padrão `http://localhost:8000`). Rode o
backend em **8010** e ajuste a variável, porque a 8000 costuma estar ocupada pelo
`mkdocs serve` do projeto:

```bash
echo 'NEXT_PUBLIC_API_URL=http://localhost:8010' > frontend/.env.local
```
