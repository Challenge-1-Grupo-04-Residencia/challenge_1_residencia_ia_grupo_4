# MVP

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |
    | 21/09 | 1.1 | MVP passa a ser recortado por requisitos | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |
    | 21/09 | 1.2 | Recorte do MVP ajustado à revisão dos RF | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

!!! warning "Proposta do PO para validar"
    O recorte abaixo é a **proposta inicial**. O MVP final é fechado depois do
    [Planning Poker](planning-poker.md): se os pontos estimados passarem da capacidade, os
    requisitos de menor valor por ponto saem.

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

| Épico | Requisitos no MVP |
| --- | --- |
| E1 · Chat | RF-01, RF-02, RF-03 |
| E2 · Persona | RF-05, RNF-08, RNF-09, RNF-20 |
| E3 · Pipeline | RF-06, RF-07, RF-08, RF-09, RF-10, RNF-18 |
| E4 · Fontes | RF-14, RF-16, RF-17 |
| E5 · Conteúdo | RF-21, RF-22 |
| E6 · Corroboração | RF-27, RF-28, RF-29 |
| E7 · Explicabilidade | RF-32, RF-33 |
| E8 · Extensão | RF-36 |
| E9 · Celular | RNF-10 |
| E10 · Dados | RNF-06, RNF-07 |

## O que fica de fora (e por quê)

| Item | Motivo |
| --- | --- |
| App nativo | Custo alto para 2 semanas; o site responsivo cobre o uso |
| PWA e compartilhamento (RF-40, RF-41) | Próximo passo natural, mas não essencial para validar a hipótese |
| Verificação de evidência por alegação (RF-30) | A LLM já extrai alegações; o NLI por alegação é incremento |
| Intensidade emocional (RF-23) | Ainda é hipótese sem validação em PT-BR |
| Detector de texto gerado por IA (RF-25) | Sinal fraco e pouco confiável |
| Histórico e últimas notícias (E11) | Não afeta a hipótese do MVP |
| API pública de reputação (RF-20) | A API interna já existe; a pública exige autenticação, limites e documentação |

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
