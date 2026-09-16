# MVP

!!! warning "Proposta do PO para validar"
    O recorte abaixo é a **proposta inicial**. O MVP final é fechado depois do
    [Planning Poker](planning-poker.md): se os pontos estimados passarem da capacidade, as
    histórias de menor valor por ponto saem.

## Restrição de prazo

| Fase | Semanas | Período |
| --- | --- | --- |
| Engage | 1 | 07/09 a 11/09 |
| Investigate | 2 e 3 | 14/09 a 25/09 |
| **Act (desenvolvimento)** | **4 e 5** | **28/09 a 09/10** |

São **2 Sprints de uma semana** com 5 pessoas. O MVP precisa ser pequeno.

## Hipótese do MVP

> **Se** a Vera mostrar uma porcentagem de veracidade **com motivos e fontes**, em linguagem
> simples, **então** as pessoas conseguem decidir se compartilham uma notícia **e** entendem
> o porquê. Isso vale para notícias resolvidas sem LLM na maioria dos casos.

## O que entra

| Canal | No MVP |
| --- | --- |
| :material-web: **Site** | Chat "Pergunte à Vera" com persona, animações e explicação |
| :material-cellphone: **Celular** | O mesmo site, **responsivo** (sem app nativo e sem PWA) |
| :material-puzzle: **Extensão** | Versão mínima: checar a aba atual e abrir o detalhe no site |

| Épico | Histórias no MVP |
| --- | --- |
| E1 · Chat | US-1.1, US-1.2, US-1.3 |
| E2 · Persona | US-2.1, US-2.2, US-2.3, US-2.4 |
| E3 · Pipeline | US-3.1, US-3.2, US-3.3, US-3.4 |
| E4 · Fontes | US-4.1, US-4.2, US-4.3 |
| E5 · Conteúdo | US-5.1, US-5.2 |
| E6 · Corroboração | US-6.1, US-6.2, US-6.3 |
| E7 · Explicabilidade | US-7.1, US-7.2 |
| E8 · Extensão | US-8.1 |
| E9 · Celular | US-9.1 |
| E10 · Dados | US-10.1, US-10.2, US-10.3 |

## O que fica de fora (e por quê)

| Item | Motivo |
| --- | --- |
| App nativo (RF-39) | Custo alto para 2 semanas; o site responsivo cobre o uso |
| PWA e compartilhamento (US-9.2, US-9.3) | Próximo passo natural, mas não essencial para validar a hipótese |
| NLI completo (US-6.4) | A LLM já extrai alegações (US-6.3); o NLI por alegação é incremento |
| Emoção NRC (US-5.3) | Ainda é hipótese sem validação em PT-BR |
| Detector de texto gerado por IA (US-5.5) | Sinal fraco e pouco confiável |
| Histórico e últimas notícias (E11) | Não afeta a hipótese do MVP |
| API pública de reputação (US-4.6) | A API interna já existe; a pública exige autenticação, limites e documentação |

## Sugestão de Sprints

=== "Sprint 1 · 28/09 a 02/10"

    **Objetivo:** checar uma notícia de ponta a ponta **sem LLM**.

    - E10: datasets, conjunto de avaliação e script de métricas
    - E4: base de fontes, RDAP e Fact Check API
    - E5: classificador TF-IDF e sensacionalismo
    - E3: extração, fórmula e orquestrador N0–N2
    - E2: persona, frases e guia visual
    - E1: chat básico ligado à API

=== "Sprint 2 · 05/10 a 09/10"

    **Objetivo:** Vera completa, explicável e em três canais.

    - E6: corroboração (N3) e extração de alegações por LLM (N4)
    - E3: regras RN-01 a RN-04
    - E7: resultado com explicação e detalhamento dos sinais
    - E2: animações e humores
    - E8: extensão mínima
    - E9: ajustes de responsividade
    - E10: calibração dos pesos e relatório final de métricas

## Critério de sucesso do MVP

- [ ] Uma notícia enviada por link recebe resultado com porcentagem, motivos e fontes
- [ ] F1 macro ≥ 0,80 no conjunto de avaliação (RNF-06)
- [ ] ≥ 60% das checagens do conjunto de avaliação resolvidas sem LLM (RNF-04)
- [ ] Funciona no celular (360 px) e na extensão do Chrome
- [ ] Teste com pelo menos 5 usuários reais: ≥ 4 entendem **por que** a Vera deu aquele resultado
