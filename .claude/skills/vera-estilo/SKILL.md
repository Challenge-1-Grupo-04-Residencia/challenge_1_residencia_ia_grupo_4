---
name: vera-estilo
description: O sistema visual da Senhora Vera — estilo cordel/quadrinho, paleta, tipografia, tokens de cor, espaço, raio e sombra, temas claro e escuro. Use SEMPRE que for criar ou alterar qualquer coisa visual no frontend: componente novo, tela nova, ajuste de cor, espaçamento, fonte, borda, sombra ou animação. Também ao escolher classe do Tailwind, ao decidir tamanho de texto, ao montar layout, e sempre que aparecerem as palavras "estilo", "design", "cor", "tema", "token", "fonte", "tipografia", "layout", "componente", "CSS", "Tailwind", "claro e escuro" ou "dark mode". Na dúvida sobre qual valor usar, consulte esta skill em vez de inventar um valor solto.
---

# O visual da Senhora Vera

## A direção: cordel, não comic americano

A referência não é HQ de super-herói. É **literatura de cordel** — a tradição gráfica do
próprio Nordeste da Vera: xilogravura em tinta preta, papel barato e quente, tipografia
de capa de folheto que grita a notícia, tudo feito para ser lido na feira.

Isso resolve o problema estético de origem: uma checadora de fatos pernambucana desenhada
como Marvel seria genérica e importada. Desenhada como cordel, ela é de algum lugar.

O que vem do cordel:

- **traço preto grosso e imperfeito** — contorno de xilogravura, não borda de 1px
- **papel quente**, nunca branco clínico
- **vermelho e ocre** sobre preto, que é a paleta de folheto de feira
- **título grande e apertado**, como manchete de capa de cordel

O que vem do quadrinho (e está no mockup): **balões de fala com rabicho**, retícula de
pontos, e riscos de ênfase à mão em volta do que importa.

Uma regra que evita o exagero: **o traço grosso é para o que fala**. Balão da Vera, botão
principal, selo de veredito. Card de lista, campo de formulário e navegação ficam
discretos — se tudo tem contorno preto de 3px, nada tem.

## Tipografia

Três famílias, cada uma com um trabalho. Todas com suporte a `latin-ext`, porque
português tem `ã`, `õ`, `ç` e acento agudo — fonte que quebra acento está descartada de
saída.

| Papel | Família | Por quê |
| --- | --- | --- |
| **Display** — títulos, veredito, números | **Baloo 2** | Pesada e arredondada, com a densidade de capa de cordel sem virar caricatura. Aguenta caixa alta e número grande |
| **Texto** — corpo, interface, leitura | **Nunito** | Arredondada o bastante para conversar com a display, e legível em 14px no celular, que é onde a desinformação circula |
| **Mão** — frases da Vera, ênfases, selos | **Caveat** | Dá o traço manual do mockup. Só para trechos curtos: é bonita em uma linha, cansativa em um parágrafo |

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:ital,wght@0,400;0,600;0,700;1,400&family=Caveat:wght@600;700&display=swap" rel="stylesheet" />
```

No Next, use `next/font/google` em vez da tag: ele hospeda a fonte junto e evita o salto
de layout no carregamento.

**Caveat nunca carrega informação sozinha.** Ela é decorativa e tem contraste de leitura
mais baixo; o veredito, a porcentagem e qualquer coisa que a pessoa precise ler para
decidir vão em Baloo 2 ou Nunito.

### Escala de tamanho

Razão 1,25 (terça maior), ancorada em 16px. Salta o suficiente para haver hierarquia
clara sem precisar de dez degraus.

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

Altura de linha: 1,5 para corpo, 1,15 para display. Display apertada é o que dá a
compressão de manchete de cordel.

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

O preto é quente (`#1A1410`) porque tinta de xilogravura sobre papel barato nunca é
neutra. `#000000` puro deixaria a tela com cara de terminal.

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

**Cor nunca é o único portador da informação.** Todo selo traz o rótulo escrito junto, e
um ícone de forma distinta — 8% dos homens têm alguma daltonia, e vermelho/verde é
exatamente o eixo que eles perdem.

## Espaço, raio e traço

Espaço em base 4, que é o que o Tailwind já usa:

| Token | px | Uso |
| --- | --- | --- |
| `--e-1` | 4 | dentro de selo |
| `--e-2` | 8 | entre ícone e texto |
| `--e-3` | 12 | dentro de botão |
| `--e-4` | 16 | padding padrão de card |
| `--e-6` | 24 | entre blocos |
| `--e-8` | 32 | entre seções |
| `--e-12` | 48 | respiro de topo de tela |

Raio — o cordel tem canto vivo, o balão tem canto redondo. A mistura é intencional:

| Token | px | Uso |
| --- | --- | --- |
| `--raio-sm` | 6 | campo, selo |
| `--raio-md` | 12 | card |
| `--raio-lg` | 20 | balão de fala |
| `--raio-total` | 999 | botão-pílula, avatar |

Traço:

| Token | Valor | Uso |
| --- | --- | --- |
| `--traco-fino` | 1px | divisória, borda de card discreto |
| `--traco-grosso` | 3px | balão, botão principal, selo de veredito |

Sombra — dura e deslocada, como bloco de impressão, não o borrão cinza de SaaS:

```css
--sombra-bloco: 4px 4px 0 var(--tinta);   /* elementos com traço grosso */
--sombra-card: 0 2px 8px rgb(26 20 16 / 0.10);  /* cards discretos */
```

## Os dois temas

Claro é o padrão: papel kraft com tinta preta é a metáfora do cordel. Escuro inverte para
papel escurecido, mantendo o calor — **não** vira cinza-azulado.

Declare os tokens em `:root`, redeclare sob `@media (prefers-color-scheme: dark)` com
guarda para a escolha manual, e de novo em `[data-tema="escuro"]`:

```css
:root { --papel: #FDF6EC; --tinta: #1A1410; }

@media (prefers-color-scheme: dark) {
  :root:not([data-tema="claro"]) { --papel: #171310; --tinta: #F7F1E8; }
}

:root[data-tema="escuro"] { --papel: #171310; --tinta: #F7F1E8; }
```

Essa ordem respeita a preferência do sistema **e** deixa a pessoa trocar na mão. Sempre
dê `background` explícito ao `body`: sem isso, o tema escuro mostra uma faixa branca no
overscroll.

No escuro, reduza o peso do traço preto — contorno grosso claro sobre fundo escuro
"vibra". Use `--traco-grosso: 2px` no tema escuro.

## Componentes e seus tokens

| Componente | Traço | Raio | Sombra | Fonte |
| --- | --- | --- | --- | --- |
| Balão da Vera | grosso | `lg` | bloco | Nunito 16–20px |
| Botão principal | grosso | `total` | bloco | Baloo 2 600 |
| Botão secundário | fino | `total` | nenhuma | Nunito 600 |
| Card do feed | fino | `md` | card | Nunito |
| Selo de veredito | grosso | `sm` | nenhuma | Baloo 2 700, caixa alta |
| Campo de texto | fino | `md` | nenhuma | Nunito 16px |
| Navegação lateral | nenhum | `md` | nenhuma | Nunito 600 |

Campo de texto em **16px no mínimo**: abaixo disso o Safari no iPhone dá zoom automático
ao focar, e a tela salta.

## Movimento

Um momento orquestrado vale mais que efeito em tudo. O momento da Vera é **o veredito
chegando**: o balão entra, a barra de veracidade preenche, a expressão dela muda. Só isso.

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

Quem marcou essa preferência costuma ter enxaqueca vestibular ou epilepsia fotossensível.
Não é preferência estética.

## Piso de qualidade

- responsivo a partir de **360px** (RNF-10) — o celular é o caso principal, não a borda
- foco de teclado visível, com contorno de 3px em `--vermelho`, jamais `outline: none`
- contraste mínimo 4,5:1 para texto; o ocre sobre papel claro **não passa** — use
  `--tinta` sobre ocre, nunca o contrário
- `prefers-reduced-motion` respeitado
- toque de no mínimo 44×44px

## Onde isto vive no código

Tokens: `frontend/src/app/globals.css`, em `@theme` do Tailwind v4.
Mapeamento de faixa para cor e humor: `frontend/src/lib/veracidade.ts`.
Voz e vocabulário dos textos: skill `vera-voz`.

Ao criar componente, **use os tokens**, não valores soltos. `p-4` e `rounded-md` puxam a
escala; `p-[17px]` e `rounded-[13px]` quebram o sistema e ninguém percebe até a terceira
tela estar fora de alinhamento.
