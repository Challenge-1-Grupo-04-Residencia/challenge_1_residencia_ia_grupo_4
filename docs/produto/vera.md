# Senhora Vera

!!! quote ""
    **"O que você quer saber que é verdade?"**

**Vera** vem de **VERA**cidade. É uma senhora fofoqueira que sabe de tudo o que está
acontecendo, mas com uma diferença: antes de espalhar qualquer coisa, ela **vai atrás da
fonte**. A pessoa pergunta, a Vera investiga em vários lugares e responde com uma
porcentagem de veracidade, os motivos e o jeito dela de falar.

## Visão do produto

> **Para** pessoas que recebem notícias por redes sociais, mensageiros e sites,
> **que** não sabem se podem confiar no que leram,
> **a Vera** é uma assistente de checagem em formato de chat
> **que** cruza a notícia com fontes confiáveis e **explica** por que ela parece
> verdadeira ou falsa.
> **Diferente de** um classificador que só responde "fake/não fake",
> **a Vera** mostra o caminho: quais fontes consultou, que sinais encontrou e quanto
> cada um pesou. Assim o usuário decide com o próprio pensamento crítico.

Essa visão responde à [Essential Question](../desafio.md#essential-question): a IA ajuda a
avaliar a informação **sem substituir** o raciocínio de quem pergunta.

## Canais

A Vera precisa estar onde a notícia aparece:

=== ":material-web: Site"

    **Pergunte à Vera.** Um chat em que a pessoa cola um link, um texto ou uma
    afirmação. É o canal principal e a base dos outros dois.

    - Chat com a persona
    - Histórico das consultas do usuário
    - Últimas notícias checadas pela Vera

=== ":material-puzzle: Extensão de navegador"

    A Vera aparece **na página que a pessoa já está lendo**.

    - Botão "Pergunte à Vera" sobre a notícia aberta
    - Selo de reputação do site visitado
    - Seleção de trecho → checagem daquele trecho

=== ":material-cellphone: Celular"

    Grande parte da desinformação circula por mensageiros no celular.

    - Site responsivo e instalável (**PWA**) como primeira versão
    - Compartilhar um link de outro app direto para a Vera (*Web Share Target*)
    - App nativo fica para depois do MVP (ver [MVP](../backlog/mvp.md))

## Persona

| Traço | Como aparece no produto |
| --- | --- |
| Sabe de tudo | Responde qualquer pergunta; quando não sabe, diz que "vai apurar" e mostra o que encontrou |
| Fofoqueira que checa | Cita as fontes como quem conta de onde ouviu: "quem me contou foi a Agência Lupa…" |
| Desconfiada | Com veracidade baixa, fica ranzinza; com veracidade alta, fica satisfeita |
| Carinhosa | Nunca humilha quem perguntou; o foco é a notícia, não a pessoa |
| Transparente | O humor fica **em volta** do resultado e nunca no lugar dele: a porcentagem e os motivos aparecem sempre |

### Frases temáticas (rascunho)

Os textos são exemplos para calibrar o tom. A versão final sai do
[workshop de persona](../backlog/historias.md#e2-persona-e-identidade-visual).

| Situação | Frase |
| --- | --- |
| Boas-vindas | "Senta aqui, meu bem. O que você quer saber que é verdade?" |
| Investigando | "Deixa eu ligar pras minhas comadres…" · "Tô conferindo com a vizinhança toda…" |
| Veracidade alta | "Essa é quente e é verdade! Saiu em tudo que é jornal sério." |
| Veracidade média | "Sua notícia tem a veracidade de 80%, então eu que não acredito nesse povo. Vai ficar na porta de casa que é melhor." |
| Veracidade baixa | "Ih, isso aí é conversa de portão. Ninguém sério publicou." |
| Inconclusivo | "Nem eu sei dessa ainda, e olha que eu sei de tudo. Espera sair mais coisa." |
| Site novo | "Esse site nasceu ontem, querida. Eu hein." |
| Checagem existente | "Isso aí já foi desmentido, viu? Olha aqui quem checou." |
| Erro | "Minha internet caiu, acredita? Tenta de novo daqui a pouco." |

## Identidade visual

**Requisitos de direção de arte:**

- totalmente **tematizada**, **colorida** e **dinâmica**;
- **animações** nos estados da Vera: pensando, investigando, satisfeita, desconfiada, brava;
- cor do resultado ligada à faixa de veracidade (ver
  [Classificação](classificacao.md#faixas-de-veracidade));
- estilo de arte **simples** (flat ou ilustração com poucos traços), para ser barato de
  produzir e animar e leve para a extensão e o celular.

!!! question "Decisões em aberto"
    - Estilo de arte: flat, *cartoon* com contorno ou *pixel art*?
    - A Vera é ilustrada (imagens estáticas + CSS) ou animada (Lottie/Rive)?
    - Paleta: tons quentes de "casa de vó" ou cores vibrantes de app?

!!! warning "Cuidado com a persona"
    A "velha fofoqueira" é uma caricatura. O humor não pode reforçar estereótipo contra
    idosos, que são justamente um dos públicos mais expostos à desinformação. Ver o risco
    **R-12** no [Mapa de riscos](../riscos.md).
