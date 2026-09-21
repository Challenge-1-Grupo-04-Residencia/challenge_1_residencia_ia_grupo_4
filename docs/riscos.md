# Mapa de riscos

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |
    | 21/09 | 1.1 | Remoção das histórias de usuário e ajuste das referências | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

**Probabilidade (P)** e **Impacto (I)** de 1 a 5. **Exposição = P × I.**
:material-circle:{ style="color: #c62828" } Alta (≥ 15) ·
:material-circle:{ style="color: #f9a825" } Média (8–14) ·
:material-circle:{ style="color: #2e7d32" } Baixa (≤ 7)

## Matriz

| P ↓ / I → | **1** | **2** | **3** | **4** | **5** |
| --- | --- | --- | --- | --- | --- |
| **5** | | | | | |
| **4** | | | R-09 | R-01 · R-03 | R-02 |
| **3** | | | R-10 · R-12 | R-04 · R-05 · R-07 · R-11 | R-06 |
| **2** | | | R-13 | R-08 | R-14 |
| **1** | | | | | |

## Registro de riscos

| ID | Risco | Categoria | P | I | Exp. | Mitigação | Gatilho | Dono |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **R-02** | **Prazo**: 2 Sprints não bastam para 3 canais + pipeline completo | Projeto | 4 | 5 | :material-circle:{ style="color: #c62828" } 20 | MVP enxuto; extensão mínima; celular = site responsivo; cortar por prioridade do Planning Poker | Sprint 1 entrega < 70% do comprometido | PO |
| **R-01** | **Falso positivo**: Vera diz que notícia verdadeira é falsa e desacredita um veículo sério | Produto / Ética | 4 | 4 | :material-circle:{ style="color: #c62828" } 16 | RN-12 (nada de certeza absoluta); faixa "Inconclusiva"; RN-10; botão de contestação | Precisão da classe "falsa" < 0,85 | Dev |
| **R-03** | **Dataset** em PT-BR pequeno, desatualizado ou enviesado; modelo não generaliza para notícias atuais | Dados | 4 | 4 | :material-circle:{ style="color: #c62828" } 16 | Combinar datasets; separar teste por data; não depender só do N2 | F1 em notícias recentes < F1 no dataset − 0,1 | Dev |
| **R-06** | **Prompt injection**: página analisada manipula a LLM | Segurança | 3 | 5 | :material-circle:{ style="color: #c62828" } 15 | RNF-12; conteúdo como dado delimitado; saída em JSON validado; LLM não decide o score sozinha | Teste com página maliciosa altera o resultado | Dev |
| **R-04** | **APIs externas** (Fact Check, busca, RDAP) com limites, custo, mudança de termos ou fora do ar | Técnico | 3 | 4 | :material-circle:{ style="color: #f9a825" } 12 | RN-06 (sinal sem dado sai do cálculo); cache; RNF-15; levantar limites na Investigate | Erro/limite > 5% das chamadas | Dev |
| **R-05** | **Custo de LLM** estoura o orçamento | Custo | 3 | 4 | :material-circle:{ style="color: #f9a825" } 12 | Pipeline em camadas; teto diário (RNF-05); modo econômico; modelo pequeno onde der | Gasto diário > 80% do teto | SM |
| **R-07** | **Pesos arbitrários**: a porcentagem não reflete a veracidade real | Produto | 3 | 4 | :material-circle:{ style="color: #f9a825" } 12 | Calibração com dados (RNF-07); histórico de calibração; comunicar como estimativa | ECE > 0,15 | Dev |
| **R-11** | **Base de fontes enviesada**: classificação de veículos vista como política | Ética / Reputação | 3 | 4 | :material-circle:{ style="color: #f9a825" } 12 | Critérios públicos e objetivos (IFCN, histórico de checagens); RN-08 (viés não pontua) | Contestação por viés político | PO |
| **R-09** | **Scraping** bloqueado (paywall, anti-bot, JS pesado) | Técnico | 4 | 3 | :material-circle:{ style="color: #f9a825" } 12 | Fallback: usuário cola o texto; extração via metadados (OpenGraph); respeitar `robots.txt` | Extração falha em > 20% das URLs de teste | Dev |
| **R-10** | **Latência** alta nas camadas N3–N4 torna o chat frustrante | UX | 3 | 3 | :material-circle:{ style="color: #f9a825" } 9 | Progresso em tempo real (RF-03); paralelizar chamadas; cache | p95 > 25 s | Dev |
| **R-12** | **Persona ofensiva**: humor da "velha fofoqueira" reforça estereótipo contra idosos | Ética / UX | 3 | 3 | :material-circle:{ style="color: #f9a825" } 9 | Revisão das frases (RNF-20); teste com usuários idosos; RN-11 | Feedback negativo no teste de usabilidade | PO |
| **R-08** | **LGPD**: dados pessoais nas notícias ou consultas enviados a terceiros | Legal | 2 | 4 | :material-circle:{ style="color: #f9a825" } 8 | RNF-11; histórico local/anônimo; não enviar identificadores à LLM | Dado pessoal identificado em log | SM |
| **R-13** | **Aprovação da extensão** na Chrome Web Store demora | Projeto | 2 | 3 | :material-circle:{ style="color: #2e7d32" } 6 | Demonstrar a extensão em modo desenvolvedor (instalação local) | — | Dev |
| **R-14** | **Uso indevido**: resultado da Vera usado como "prova" para atacar veículos ou pessoas | Ética | 2 | 5 | :material-circle:{ style="color: #f9a825" } 10 | Resultado sempre com ressalvas e fontes; nenhum rótulo absoluto; aviso de uso | Print da Vera usado fora de contexto | PO |

## Acompanhamento

O Scrum Master revisa esta página na **Sprint Review**:

- gatilho disparado → o risco vira item de impedimento na Daily;
- riscos novos entram com `R-<próximo número>`;
- riscos encerrados permanecem na tabela, com a exposição riscada.
