# Planning Poker

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |
    | 21/09 | 1.1 | Estimativa passa a ser por requisito | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |
    | 21/09 | 1.2 | Planilha ajustada à revisão dos RF | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

A equipe estima o **esforço** de cada requisito com Planning Poker e o PO atribui o **valor**.
A combinação dos dois alimenta a **Matriz de Esforço × Valor** definida na
[Metodologia](../metodologia.md#artefatos) e decide a ordem do backlog e o corte do
[MVP](mvp.md).

## Escala

Sequência de Fibonacci modificada:

| Carta | Significado |
| --- | --- |
| **0** | Já está feito / trivial |
| **1 · 2 · 3** | Pequena, bem entendida |
| **5 · 8** | Média, com alguma incerteza |
| **13** | Grande: limite para caber em uma Sprint |
| **21** | Grande demais: **quebrar** o requisito antes de estimar de novo |
| **?** | Não entendi o requisito: volta para o PO |
| **:material-coffee:** | Pausa |

!!! tip "Requisito de referência"
    Antes da primeira rodada, a equipe escolhe um requisito conhecido e o fixa como **3
    pontos**. Todos os outros são estimados **em relação a ele**. Sugestão:
    **RF-16** (consultar a idade do domínio).

## Como conduzir uma rodada

1. **PO** lê o requisito e o que se espera dele.
2. A equipe tira dúvidas (máx. 2 min). Se algo não estiver claro, carta **?** e o requisito volta.
3. Cada Developer escolhe uma carta **em segredo**.
4. Todos revelam **ao mesmo tempo**.
5. Se houver consenso (ou diferença de uma carta vizinha), registra o maior valor.
6. Se houver divergência, **quem votou o maior e o menor explica** o raciocínio.
7. Nova votação. Após **3 rodadas** sem consenso, o **Scrum Master** registra a mediana.

**Papéis:** Scrum Master (Ian) facilita e controla o tempo. PO (Maykon) esclarece e **não
vota esforço**. Developers votam.

**Ferramentas:** baralho físico, [planningpokeronline.com](https://planningpokeronline.com)
ou campo *Story Points* no GitHub Projects.

## Valor de negócio

O PO dá nota de **1 a 5** para cada requisito, considerando:

| Nota | Critério |
| --- | --- |
| **5** | Sem isso não existe produto / não responde o Challenge |
| **4** | Essencial para a hipótese do MVP |
| **3** | Melhora muito a experiência ou a qualidade da checagem |
| **2** | Incremento desejável |
| **1** | Pode esperar |

## Priorização

**Índice de prioridade** = `Valor × 10 / Story Points`. Quanto maior, antes entra.

A matriz ajuda a visualizar:

| | **Esforço baixo (≤ 5 SP)** | **Esforço alto (≥ 8 SP)** |
| --- | --- | --- |
| **Valor alto (4–5)** | :material-rocket-launch: **Fazer primeiro** | :material-calendar-check: **Planejar bem** (considerar quebrar) |
| **Valor baixo (1–3)** | :material-lightning-bolt: **Ganho rápido** se sobrar tempo | :material-close-circle: **Evitar** |

## Planilha de estimativa

Preencha durante a sessão. Os requisitos estão na ordem da proposta de MVP.

| Requisito | Resumo | MVP | Rodada 1 | Rodada 2 | **SP final** | **Valor** | **Prioridade** | Quadrante |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RNF-06 | Datasets, conjunto de avaliação e métricas | :material-check: | | | | | | |
| RNF-07 | Calibrar pesos | :material-check: | | | | | | |
| RF-14 | Confiabilidade do veículo | :material-check: | | | | | | |
| RF-15 | Manter a base curada de veículos | :material-check: | | | | | | |
| RF-16 | Idade do domínio | :material-check: | | | | | | |
| RF-17 | Checagens já publicadas por agências | :material-check: | | | | | | |
| RF-21 | Classificação pelo estilo de escrita | :material-check: | | | | | | |
| RF-22 | Sensacionalismo | :material-check: | | | | | | |
| RF-06 | Extração de conteúdo da URL | :material-check: | | | | | | |
| RF-07 | Checagem em camadas | :material-check: | | | | | | |
| RF-08 | Regra de parada | :material-check: | | | | | | |
| RF-09 | Score de veracidade e confiança | :material-check: | | | | | | |
| RF-10 | Regras que se sobrepõem ao score | :material-check: | | | | | | |
| RNF-18 | Pesos configuráveis | :material-check: | | | | | | |
| RF-27 | Busca de notícias semelhantes | :material-check: | | | | | | |
| RF-28 | Contagem de veículos confiáveis | :material-check: | | | | | | |
| RF-29 | Extração de alegações checáveis | :material-check: | | | | | | |
| RF-05 | Reação da Vera por faixa | :material-check: | | | | | | |
| RNF-20 | Experiência tematizada | :material-check: | | | | | | |
| RNF-08 | Acessibilidade | :material-check: | | | | | | |
| RNF-09 | Resultado não depende só de cor | :material-check: | | | | | | |
| RF-01 | Enviar link, texto ou afirmação | :material-check: | | | | | | |
| RF-02 | Resposta em chat | :material-check: | | | | | | |
| RF-03 | Andamento da investigação | :material-check: | | | | | | |
| RF-32 | Resultado com motivos e fontes | :material-check: | | | | | | |
| RF-33 | Detalhamento dos sinais | :material-check: | | | | | | |
| RF-36 | Extensão: checar a aba atual | :material-check: | | | | | | |
| RNF-10 | Uso no celular (360 px) | :material-check: | | | | | | |
| RF-04 | Perguntas de acompanhamento | | | | | | | |
| RF-11 | Reaproveitar checagens (cache) | | | | | | | |
| RF-12 | Modo econômico sem LLM | | | | | | | |
| RF-13 | Dificuldade da checagem | | | | | | | |
| RF-18 | Histórico de falsas por domínio | | | | | | | |
| RF-19 | Domínios impostores | | | | | | | |
| RF-20 | API pública de reputação | | | | | | | |
| RF-23 | Intensidade emocional | | | | | | | |
| RF-24 | Citação de fontes verificáveis | | | | | | | |
| RF-25 | Texto gerado por IA | | | | | | | |
| RF-26 | Sátira e opinião | | | | | | | |
| RF-30 | Evidência por alegação | | | | | | | |
| RF-31 | Cópia alterada | | | | | | | |
| RF-34 | Dicas de pensamento crítico | | | | | | | |
| RF-35 | Contestar resultado | | | | | | | |
| RF-37 | Selo de reputação | | | | | | | |
| RF-38 | Checar trecho selecionado | | | | | | | |
| RF-39 | Transcrição de vídeo do YouTube | | | | | | | |
| RF-40 | PWA instalável | | | | | | | |
| RF-41 | Compartilhar de outro app | | | | | | | |
| RNF-04 | % resolvida sem LLM | | | | | | | |
| RF-42 | Histórico do usuário | | | | | | | |
| RF-43 | Últimas notícias | | | | | | | |

## Capacidade da Sprint

| Sprint | Pessoas | Dias úteis | Velocidade estimada (SP) | SP comprometidos |
| --- | --- | --- | --- | --- |
| Sprint 1 (28/09 a 02/10) | 5 | 5 | | |
| Sprint 2 (05/10 a 09/10) | 5 | 5 | | |

!!! note "Primeira Sprint sem histórico"
    Sem velocidade histórica, comprometa no máximo **70%** do que parece caber e ajuste na
    Sprint 2 com a velocidade real da Sprint 1.

## Registro das sessões

| Data | Participantes | Requisitos estimados | Observações |
| --- | --- | --- | --- |
| | | | |
