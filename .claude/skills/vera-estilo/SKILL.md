---
name: vera-estilo
description: O sistema visual da Senhora Vera — quadrinho de banca com raiz de cordel, paleta, tipografia, tokens de cor, espaço, raio e sombra, painéis, balões, retícula, temas claro e escuro. Use SEMPRE que for criar ou alterar qualquer coisa visual no frontend: componente novo, tela nova, ajuste de cor, espaçamento, fonte, borda, sombra, ilustração ou animação. Também ao escolher classe do Tailwind, ao decidir tamanho de texto, ao montar layout, ao usar as imagens da Vera, e sempre que aparecerem as palavras "estilo", "design", "cor", "tema", "token", "fonte", "tipografia", "layout", "componente", "CSS", "Tailwind", "quadrinho", "HQ", "claro e escuro" ou "dark mode". Na dúvida sobre qual valor usar, consulte esta skill em vez de inventar um valor solto.
---

# O visual da Senhora Vera

## A direção: quadrinho de banca, com raiz de cordel

A Vera é desenhada como **quadrinho popular** — traço preto grosso, cor chapada,
painéis com moldura, balão com rabicho, retícula de pontos e letreiro de capa. É a
linguagem gráfica que a arte da personagem já traz (ver `frontend/public/vera-*.png`):
contorno pesado, pele em laranja chapado, vestido florido vermelho sobre preto.

A raiz continua sendo **cordel**: papel quente em vez de branco clínico, vermelho e
ocre sobre preto, manchete apertada de folheto de feira. O que mudou foi o sotaque do
traço — de xilogravura para quadrinho —, porque é assim que a Vera foi desenhada, e a
interface tem de combinar com a personagem, não discutir com ela.

O que isso significa na prática:

- **traço preto grosso** no que fala: painel, balão, botão principal, selo de veredito
- **papel quente**, nunca branco clínico
- **vermelho e ocre** sobre preto quente
- **letreiro de quadrinho** nos títulos, veredito e números
- **retícula de pontos** nas faixas de destaque, como a trama de impressão barata
- **sombra dura e deslocada**, de bloco impresso, nunca o borrão cinza de SaaS

A regra que evita o exagero continua valendo: **o traço grosso é para o que fala**.
Card de lista, campo de formulário e navegação ficam discretos — se tudo tem contorno
preto de 3px, nada tem.

## Tipografia

Três famílias, cada uma com um trabalho. Todas com suporte a `latin-ext`, porque
português tem `ã`, `õ`, `ç` e acento agudo — fonte que quebra acento está descartada de
saída. (Foi o que tirou a **Comic Neue** da disputa: só tem `latin`.)

| Papel | Família | Por quê |
| --- | --- | --- |
| **Display** — títulos, veredito, números, selo | **Bangers** | É o letreiro de quadrinho: condensada, caixa alta, com a energia de capa de HQ. Carrega manchete e porcentagem grande sem parecer software |
| **Texto** — corpo, interface, leitura | **Nunito** | Arredondada o bastante para conversar com a display, e legível em 14px no celular, que é onde a desinformação circula |
| **Mão** — frases da Vera, ênfases | **Patrick Hand** | Letra de letreirista de quadrinho, não caligrafia de convite. Só para trechos curtos |

```tsx
// Sempre next/font/google, nunca a tag <link>: ele hospeda junto e evita o
// salto de layout no carregamento.
import { Bangers, Nunito, Patrick_Hand } from "next/font/google";
```

**Bangers só tem um peso (400) e é desenhada em caixa alta.** Não peça `font-bold`
dela: o negrito sai sintético e suja o traço. Para ela respirar, use
`letter-spacing: 0.02em` e `line-height: 1.05` — já embutidos em `.fonte-display`.

**Patrick Hand nunca carrega informação sozinha.** Ela é decorativa e tem contraste de
leitura mais baixo; o veredito, a porcentagem e qualquer coisa que a pessoa precise ler
para decidir vão em Bangers ou Nunito.

### Escala de tamanho

Razão 1,25 (terça maior), ancorada em 16px.

| Token | Tamanho | Uso |
| --- | --- | --- |
| `--texto-xs` | 12px | metadado, rodapé de card |
| `--texto-sm` | 14px | apoio, legenda, dica de campo |
| `--texto-base` | 16px | corpo — **nunca menor que isto para texto de leitura** |
| `--texto-lg` | 20px | fala da Vera no balão |
| `--texto-xl` | 25px | título de seção |
| `--texto-2xl` | 31px | título de tela |
| `--texto-3xl` | 39px | veredito, porcentagem |
| `--texto-4xl` | 49px | manchete de capa |

Altura de linha: 1,5 para corpo, 1,05 para a display. A Bangers é alta e estreita:
em tamanho pequeno ela some, então **não use display abaixo de 20px** — para rótulo
miúdo, Nunito 600 em caixa alta faz o serviço.

## Cor

### Marca

| Token | Claro | Escuro | Papel |
| --- | --- | --- | --- |
| `--vermelho` | `#C1121F` | `#E63946` | cor da Vera: sidebar, botão principal, selo |
| `--vermelho-forte` | `#8B0A14` | `#C1121F` | estado pressionado, texto sobre claro |
| `--ocre` | `#E8A020` | `#F4B942` | destaque secundário, "em análise" |
| `--tinta` | `#1A1410` | `#F7F1E8` | traço e texto — preto **quente**, nunca `#000` |
| `--papel` | `#FDF6EC` | `#171310` | fundo: kraft claro / kraft escuro |
| `--papel-2` | `#FFFFFF` | `#221C17` | cartão sobre o fundo |

O preto é quente porque tinta sobre papel barato nunca é neutra. `#000000` puro
deixaria a tela com cara de terminal.

### Faixas de veracidade

Vêm de `docs/produto/classificacao.md` e **não são negociáveis**: a cor comunica o
resultado.

| Faixa | Claro | Escuro |
| --- | --- | --- |
| Provavelmente falsa | `#C62828` | `#EF5350` |
| Duvidosa | `#EF6C00` | `#FFA726` |
| Inconclusiva | `#F9A825` | `#FFD54F` |
| Provavelmente verdadeira | `#7CB342` | `#9CCC65` |
| Confirmada por fontes | `#2E7D32` | `#66BB6A` |

**Cor nunca é o único portador da informação.** Todo selo traz o rótulo escrito junto e
um pictograma de forma distinta — 8% dos homens têm alguma daltonia, e vermelho/verde é
exatamente o eixo que eles perdem. Como o público da Vera inclui quem lê com
dificuldade, o pictograma não é enfeite: muitas vezes é o que vai ser lido primeiro.
Como desenhar isso está em `vera-gamificacao`.

## Espaço, raio e traço

Espaço em base 4, que é o que o Tailwind já usa: `--e-1` 4px · `--e-2` 8 · `--e-3` 12 ·
`--e-4` 16 · `--e-6` 24 · `--e-8` 32 · `--e-12` 48.

Raio — o painel tem canto vivo, o balão tem canto redondo. A mistura é intencional:

| Token | px | Uso |
| --- | --- | --- |
| `--raio-sm` | 6 | campo, selo |
| `--raio-md` | 12 | card |
| `--raio-lg` | 20 | balão de fala |
| `--raio-total` | 999 | botão-pílula, avatar |

Traço: `--traco-fino` 1px para divisória e card discreto; `--traco-grosso` 3px para
painel, balão, botão principal e selo de veredito.

Sombra dura e deslocada, como bloco de impressão:

```css
--sombra-bloco: 4px 4px 0 var(--tinta);
--sombra-bloco-sm: 2px 2px 0 var(--tinta);
--sombra-card: 0 2px 8px rgb(26 20 16 / 0.10);
```

## Os elementos de quadrinho

Três utilitários em `globals.css` carregam a linguagem. Use-os em vez de repetir
classes soltas de borda e sombra:

| Classe | O que é | Onde usar |
| --- | --- | --- |
| `.painel` | moldura preta grossa com sombra de bloco | o quadro do veredito, o quadro da investigação, a abertura |
| `.reticula` | trama de pontos da impressão barata | fundo de faixa de destaque, nunca atrás de texto corrido |
| `.fonte-mao` | Patrick Hand | fala curta da Vera, ênfase manuscrita |

O **balão** é componente (`ui/Balao.tsx`), não classe: o rabicho precisa de dois
triângulos sobrepostos para herdar a cor do tema.

A **retícula sobre texto** é proibida: ela derruba o contraste e é justamente quem lê
com dificuldade que paga a conta.

## As imagens da Vera

A personagem é PNG, não mais SVG desenhado em código. Três arquivos em
`frontend/public/`, cada um com um papel:

| Arquivo | Pose | Onde |
| --- | --- | --- |
| `vera-rosto.png` | só o rosto, de 3/4 | avatar do chat, selo, lista |
| `vera-corpo-apontando.png` | dedo em riste, didática | abertura, estado vazio, dica |
| `vera-corpo.png` | mão no queixo, avaliando | investigando, resultado, erro |

Elas vêm de `frontend/arte/*-original.png`, que são os arquivos como a equipe os
exportou. O retrato de mão no queixo veio com fundo preto chapado; quem recortou foi
`frontend/scripts/recortar-fundo.py`, e o script explica no cabeçalho por que o recorte
simples por cor não serve — **o preto do fundo é o mesmo preto do contorno da arte**.
Se chegar imagem nova com fundo, rode o script, não apague na mão:

```bash
uv run python frontend/scripts/recortar-fundo.py frontend/arte/nova.png frontend/public/nova.png
```

Sempre `next/image` com `width`/`height`, nunca `<img>`: o salto de layout numa página
que a pessoa está lendo com aflição é o pior momento possível para a tela pular.

**A expressão da Vera não muda mais por atributo** — são fotos fixas. Quem carrega o
humor do resultado (RF-05) é a moldura: a cor da faixa no painel, o pictograma e o
rótulo escrito. Trocar de pose é escolher outro arquivo, e só há três.

## Movimento

Um momento orquestrado vale mais que efeito em tudo. O momento da Vera é **o veredito
chegando**: o painel entra com pique, a barra preenche, o selo carimba. Só isso.

Card de feed não faz fade ao aparecer, botão não escala no hover — isso é o default
genérico. Transição existe para mostrar **o que mudou** depois de uma ação da pessoa.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Quem marcou essa preferência costuma ter enxaqueca vestibular ou epilepsia
fotossensível. Não é preferência estética.

## Os dois temas

Claro é o padrão: papel kraft com tinta preta. Escuro inverte para papel escurecido
mantendo o calor — **não** vira cinza-azulado. Declare os tokens em `:root`, redeclare
sob `@media (prefers-color-scheme: dark)` com guarda para a escolha manual, e de novo
em `[data-tema="escuro"]`.

No escuro, reduza o traço: contorno grosso claro sobre fundo escuro "vibra". Use
`--traco-grosso: 2px`. Sempre dê `background` explícito ao `body`: sem isso, o tema
escuro mostra uma faixa branca no overscroll.

## Piso de qualidade

- responsivo a partir de **360px** (RNF-10) — o celular é o caso principal, não a borda
- foco de teclado visível, contorno de 3px em `--vermelho`, jamais `outline: none`
- contraste mínimo 4,5:1 para texto; o ocre sobre papel claro **não passa** — use
  `--tinta` sobre ocre, nunca o contrário
- `prefers-reduced-motion` respeitado
- toque de no mínimo 44×44px
- campo de texto em 16px no mínimo: abaixo disso o Safari no iPhone dá zoom ao focar

## Onde isto vive no código

Tokens e utilitários: `frontend/src/app/globals.css`, em `@theme` do Tailwind v4.
Fontes: `frontend/src/app/layout.tsx`.
Faixa → cor, pictograma e humor: `frontend/src/lib/veracidade.ts`.
Pictogramas: `frontend/src/components/ui/Icone.tsx`.
Como comunicar resultado para quem lê pouco: skill `vera-gamificacao`.
Voz e vocabulário dos textos: skill `vera-voz`.

Ao criar componente, **use os tokens**, não valores soltos. `p-4` e `rounded-md` puxam a
escala; `p-[17px]` e `rounded-[13px]` quebram o sistema e ninguém percebe até a terceira
tela estar fora de alinhamento.
