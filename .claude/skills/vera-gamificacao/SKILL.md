---
name: vera-gamificacao
description: Como a Vera mostra resultado para quem lê pouco — pictograma antes da palavra, placar da investigação, termômetro de veracidade, carimbos, poucas palavras por bloco e detalhe técnico escondido atrás de um clique. Use SEMPRE que for exibir resultado de checagem, andamento da investigação, lista de evidências, sinais, selo, medidor, barra ou qualquer número na tela. Também ao escrever rótulo curto, ao escolher ícone, ao decidir o que mostrar primeiro e o que esconder, e sempre que aparecerem as palavras "gamificar", "ícone", "pictograma", "placar", "carimbo", "medidor", "termômetro", "resultado", "evidência", "muito texto", "denso" ou "simplificar". Na dúvida sobre quanto mostrar, siga o orçamento de palavras desta skill.
---

# Mostrar resultado para quem lê pouco

## Quem está do outro lado

A desinformação circula com mais força justamente onde a leitura é mais difícil. Parte
de quem usa a Vera lê devagar, lê só o começo, ou não lê — vê. Para essa pessoa, um
parágrafo bem escrito é uma parede, e uma parede faz ela sair sem resposta.

Isso não é motivo para esconder a explicação. **RN-05 continua valendo**: resultado sem
explicação não é exibido. O que muda é a forma da explicação: ela vira **figura,
número e palavra curta**, com o texto técnico a um toque de distância para quem quiser.

A régua é simples: *dá para entender o veredito e o porquê olhando a tela por três
segundos, sem ler frase inteira?*

## A ordem de leitura

Todo resultado se lê nesta ordem, de cima para baixo. Não invente outra:

1. **A cara da Vera** — a pose já diz se a coisa é boa ou ruim
2. **O pictograma grande** — uma figura, do tamanho de um polegar
3. **A palavra do veredito** — em Bangers, caixa alta, curta
4. **O termômetro** — cinco casas, a sua acesa
5. **Três evidências** — cada uma com ícone, polegar e quatro ou cinco palavras
6. **Quem publicou** — nome do veículo com visto ou sem
7. **"Quero ver as contas"** — e só aí entra o mundo técnico

## Orçamento de palavras

Isto é limite, não sugestão. Estourou, corta:

| Elemento | Máximo |
| --- | --- |
| Palavra do veredito | 3 palavras |
| Linha de evidência | 5 palavras |
| Fala da Vera no painel | 12 palavras |
| Nome de etapa da investigação | 3 palavras |
| Rótulo de botão | 3 palavras |

Dentro do detalhamento (RF-33) o orçamento não vale: ali o objetivo é auditar, e quem
abriu pediu o texto longo.

## Pictograma: a regra que não se quebra

**Ícone nunca aparece sozinho, e palavra nunca aparece sozinha.** As duas coisas juntas,
sempre — o ícone serve quem lê pouco, a palavra serve quem não entende aquele desenho, e
o `aria-label` serve quem não vê nenhum dos dois.

- Desenho **próprio**, em SVG, de `ui/Icone.tsx`. **Emoji é proibido**: muda de cara em
  cada aparelho, some em alguns Android e o leitor de tela lê "rosto levemente
  franzido" no meio de um veredito.
- `currentColor` sempre, para o ícone acompanhar tema e faixa
- mínimo de 24px; o do veredito, 48px
- `aria-hidden` no ícone quando a palavra está do lado — senão o leitor de tela fala
  duas vezes a mesma coisa
- forma distinta por significado, não só cor: polegar para cima e para baixo têm
  silhuetas opostas, e é isso que salva quem tem daltonia

## O termômetro, e não só a porcentagem

"62%" é uma abstração. Cinco casas desenhadas, com a sua acesa e as outras apagadas,
são uma régua — e régua se lê de relance.

Mostre as duas coisas: o termômetro carrega o sentido, a porcentagem carrega a
precisão. A porcentagem continua obrigatória onde ela existe (RN-05), e continua
proibida em opinião e sátira (RN-03).

As cinco casas são as cinco faixas, na ordem de `docs/produto/classificacao.md`. Nunca
invente uma sexta, nem junte duas para "simplificar": a faixa é contrato de produto.

## Carimbo e placar — gamificação com limite

O que pode virar jogo é **o caminho da investigação**: as quatro etapas viram quatro
carimbos que a Vera vai batendo, com um placar "3 de 4". Isso dá ritmo à espera e
mostra trabalho sendo feito, que é o que a explicabilidade promete.

O que **não** pode virar jogo:

- **Pontuar a pessoa.** A Vera não dá medalha a quem checou muito. Quem checa está
  fazendo a coisa certa e pronto; transformar isso em pontuação convida a brincar com um
  assunto que, do outro lado, é uma mãe acreditando em remédio falso.
- **Comemorar o veredito.** Nada de confete, nada de "você acertou!". Muita notícia
  falsa é sobre morte, doença e eleição. A Vera comenta com humor, mas RN-11 manda: o
  humor acompanha o dado técnico, nunca o substitui.
- **Esconder o que não foi medido.** Sinal sem dado continua aparecendo como "não
  consegui apurar" (RN-06). Um placar que só mostra acerto mente sobre a cobertura.

## Progressão: resumo, depois contas

Três blocos na tela, e um botão. Dentro do botão, tudo o que hoje aparece de uma vez:
confiança, cobertura, dificuldade, sinal por sinal com peso, nome técnico, justificativa
e a lista de URLs.

Quem fecha o botão tem a resposta. Quem abre tem a auditoria. Ninguém é obrigado a
rolar por cima da auditoria para chegar na resposta — que era exatamente o problema.

## Acessibilidade

- o bloco do resultado é `role="status"` com `aria-live="polite"`: o veredito chega
  sozinho, e quem usa leitor de tela precisa ser avisado
- o termômetro é `role="meter"` com `aria-valuenow`, `aria-valuemin`, `aria-valuemax` e
  um `aria-label` que diz o que está sendo medido
- `aria-label` descreve **função**, não faz piada: "Ver as contas da checagem", não
  "Bota o olho aqui"
- toque de 44×44px no mínimo, inclusive no botão de abrir detalhe
- contraste 4,5:1 no texto e 3:1 no pictograma que carrega informação

## As palavras curtas

Elas são voz da Vera como qualquer outra (skill `vera-voz`), só que espremidas. Continua
proibido humilhar quem perguntou, continua proibido cravar certeza (RN-12), e o rótulo
oficial da faixa aparece escrito mesmo quando a palavra curta já apareceu — "MENTIRA" é
bom de ler, mas o que o produto afirma é "provavelmente falsa".

## Onde isto vive no código

Pictogramas: `frontend/src/components/ui/Icone.tsx`.
Faixa → pictograma, palavra curta, cor e pose: `frontend/src/lib/veracidade.ts`.
Sinal → ícone e frase de 4 palavras: `frontend/src/lib/linguagem.ts`.
Painel do veredito: `frontend/src/components/checagem/ResultadoChecagem.tsx`.
Placar da investigação: `frontend/src/components/checagem/CaminhoDaInvestigacao.tsx`.
Traço, cor e tipografia: skill `vera-estilo`.
