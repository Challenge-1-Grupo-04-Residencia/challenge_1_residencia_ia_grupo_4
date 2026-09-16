# Planning Poker

A equipe estima o **esforço** de cada história com Planning Poker e o PO atribui o **valor**.
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
| **21** | Grande demais: **quebrar** a história antes de estimar de novo |
| **?** | Não entendi a história: volta para o PO |
| **:material-coffee:** | Pausa |

!!! tip "História de referência"
    Antes da primeira rodada, a equipe escolhe uma história conhecida e a fixa como **3
    pontos**. Todas as outras são estimadas **em relação a ela**. Sugestão:
    **US-4.2** (consultar a idade do domínio via RDAP).

## Como conduzir uma rodada

1. **PO** lê a história e os critérios de aceite.
2. A equipe tira dúvidas (máx. 2 min). Se algo não estiver claro, carta **?** e a história volta.
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

O PO dá nota de **1 a 5** para cada história, considerando:

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

Preencha durante a sessão. As histórias estão na ordem da proposta de MVP.

| História | Resumo | MVP | Rodada 1 | Rodada 2 | **SP final** | **Valor** | **Prioridade** | Quadrante |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-10.1 | Levantar datasets | :material-check: | | | | | | |
| US-10.2 | Conjunto de avaliação + métricas | :material-check: | | | | | | |
| US-10.3 | Calibrar pesos | :material-check: | | | | | | |
| US-4.1 | Base curada de fontes | :material-check: | | | | | | |
| US-4.2 | Idade do domínio | :material-check: | | | | | | |
| US-4.3 | Checagens existentes | :material-check: | | | | | | |
| US-5.1 | Classificador TF-IDF | :material-check: | | | | | | |
| US-5.2 | Sensacionalismo | :material-check: | | | | | | |
| US-3.1 | Orquestrador em camadas | :material-check: | | | | | | |
| US-3.2 | Extração de URL | :material-check: | | | | | | |
| US-3.3 | Fórmula V e C | :material-check: | | | | | | |
| US-3.4 | Regras que sobrepõem o score | :material-check: | | | | | | |
| US-6.1 | Busca de notícias semelhantes | :material-check: | | | | | | |
| US-6.2 | Contagem de veículos confiáveis | :material-check: | | | | | | |
| US-6.3 | LLM extrai alegações | :material-check: | | | | | | |
| US-2.1 | Persona e frases | :material-check: | | | | | | |
| US-2.2 | Humores por faixa | :material-check: | | | | | | |
| US-2.3 | Guia visual | :material-check: | | | | | | |
| US-2.4 | Acessibilidade | :material-check: | | | | | | |
| US-1.1 | Enviar link/texto | :material-check: | | | | | | |
| US-1.2 | Resposta com persona | :material-check: | | | | | | |
| US-1.3 | Progresso da investigação | :material-check: | | | | | | |
| US-7.1 | Resultado com motivos e fontes | :material-check: | | | | | | |
| US-7.2 | Detalhamento dos sinais | :material-check: | | | | | | |
| US-8.1 | Extensão: checar aba | :material-check: | | | | | | |
| US-9.1 | Site responsivo | :material-check: | | | | | | |
| US-1.4 | Perguntas sobre o resultado | | | | | | | |
| US-3.5 | Cache | | | | | | | |
| US-3.6 | Modo econômico | | | | | | | |
| US-4.4 | Histórico de fakes por domínio | | | | | | | |
| US-4.5 | Domínios impostores | | | | | | | |
| US-4.6 | API pública de reputação | | | | | | | |
| US-5.3 | Emoção NRC | | | | | | | |
| US-5.4 | Citação de fontes | | | | | | | |
| US-5.5 | Texto gerado por IA | | | | | | | |
| US-5.6 | Sátira e opinião | | | | | | | |
| US-6.4 | NLI por alegação | | | | | | | |
| US-6.5 | Cópia alterada | | | | | | | |
| US-7.3 | Dicas de pensamento crítico | | | | | | | |
| US-7.4 | Contestar resultado | | | | | | | |
| US-8.2 | Selo de reputação | | | | | | | |
| US-8.3 | Checar trecho selecionado | | | | | | | |
| US-9.2 | PWA instalável | | | | | | | |
| US-9.3 | Compartilhar do WhatsApp | | | | | | | |
| US-10.4 | % resolvida sem LLM | | | | | | | |
| US-11.1 | Histórico do usuário | | | | | | | |
| US-11.2 | Últimas notícias | | | | | | | |

## Capacidade da Sprint

| Sprint | Pessoas | Dias úteis | Velocidade estimada (SP) | SP comprometidos |
| --- | --- | --- | --- | --- |
| Sprint 1 (28/09 a 02/10) | 5 | 5 | | |
| Sprint 2 (05/10 a 09/10) | 5 | 5 | | |

!!! note "Primeira Sprint sem histórico"
    Sem velocidade histórica, comprometa no máximo **70%** do que parece caber e ajuste na
    Sprint 2 com a velocidade real da Sprint 1.

## Registro das sessões

| Data | Participantes | Histórias estimadas | Observações |
| --- | --- | --- | --- |
| | | | |
