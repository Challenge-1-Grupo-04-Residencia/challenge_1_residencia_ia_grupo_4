# Frontend — site e chat da Vera

Next.js 15 (App Router) + TypeScript + Tailwind v4.

```bash
export PATH="$HOME/.local/node/bin:$PATH"   # o Node está aqui, não no Homebrew
npm install
cp .env.example .env.local                  # aponta para o backend em :8010
npm run dev                                 # http://localhost:3000
```

O backend precisa estar rodando:

```bash
cd .. && uv run uvicorn src.main:app --app-dir backend --reload --port 8010
```

## Checagem de tipos

Use `npm run build`, não `npx tsc --noEmit`. O `tsc` isolado falha com
`Cannot find name 'LayoutProps'` porque esse tipo é gerado pelo Next durante o build;
o build roda TypeScript de verdade e é o que vale.

## Estrutura

```
src/
├── app/
│   ├── layout.tsx        html lang="pt-BR", fontes, tema escuro
│   └── page.tsx          a conversa com a Vera
├── components/
│   ├── vera/
│   │   └── VeraAvatar.tsx      a persona em SVG, com expressões
│   ├── checagem/
│   │   ├── CaixaDePergunta.tsx entrada de link, texto ou afirmação (RF-01)
│   │   ├── Investigando.tsx    feedback em etapas (RF-03)
│   │   ├── ResultadoChecagem.tsx  o veredito (RF-32, RN-05)
│   │   └── DetalheSinais.tsx   sinal por sinal, com peso (RF-33)
│   └── ui/               primitivos reutilizáveis
├── lib/
│   ├── api.ts            ÚNICO ponto que fala com o backend
│   └── veracidade.ts     faixa → cor, humor da Vera, frase temática
└── types/
    └── checagem.ts       espelho do contrato da API
```

Duas fronteiras que não se atravessam:

- **Componentes não chamam `fetch`.** Importam de `lib/api.ts`, onde ficam a URL base,
  o tratamento de erro na voz da Vera e o cancelamento de requisição.
- **`types/checagem.ts` espelha `backend/src/main.py`.** Mudança de contrato altera os
  dois na mesma PR.

O frontend **não recalcula nada**: faixa, rótulo, principais sinais e dificuldade vêm
prontos da API. Duplicar a fórmula aqui garantiria divergência na primeira calibração de
pesos.

## Regras de produto que a interface tem de respeitar

Não são preferências de design — são regras de negócio:

- **RN-05** — todo resultado mostra porcentagem, faixa, principais sinais e fontes.
  Resultado sem explicação não é exibido.
- **RN-03** — opinião e sátira não recebem porcentagem. Respeite `exibe_porcentagem`;
  nada de `veracidade ?? 50`.
- **RN-11** — a frase da Vera aparece junto do dado técnico, nunca no lugar dele.
- **RN-12** — os rótulos vêm da API com "provavelmente" e "confirmada por fontes". Não
  reescreva para "verdadeira".
- **RF-33** — o detalhamento mostra **também** os sinais indisponíveis. Esconder o que a
  Vera não mediu faria a checagem parecer mais completa do que foi.

## Persona

`estiloDaFaixa(faixa)` em `lib/veracidade.ts` mapeia faixa de veracidade → humor, cor e
frase. Para mudar a reação da Vera, mexa nessa tabela: ela também alimenta o
`VeraAvatar`, e duplicar o mapeamento faz avatar e cor divergirem.

O avatar é SVG inline em vez de imagem porque a extensão de navegador e o PWA precisam
de algo leve, e trocar de expressão passa a ser mudança de atributo.

Frases e direção de arte estão em `origin/docs:docs/produto/vera.md`.

## Acessibilidade

RNFs, não extras. O site atende a partir de **360 px** (RNF-10) — grande parte da
desinformação circula por mensageiro no celular, então o celular é o caso principal.

Estados de carregamento usam `role="status"` com `aria-live`, a barra de veracidade é
`role="meter"` com `aria-valuenow`, o avatar tem `aria-label` descrevendo a expressão, e
cor nunca é o único portador de informação: a faixa vem sempre escrita também.

## Pendente

Feed de últimas checagens (RF-43), histórico do usuário (RF-42) e perguntas de
acompanhamento (RF-04) são issues em aberto. O `Investigando` avança as etapas por tempo
estimado porque a API ainda responde só no fim — quando houver streaming, troque o
temporizador pelo evento real.
