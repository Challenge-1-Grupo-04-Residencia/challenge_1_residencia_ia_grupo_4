# Visão geral do backlog

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |
    | 21/09 | 1.1 | Remoção das histórias de usuário e ajuste das referências | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

O Product Backlog segue a hierarquia **Temas → Épicos → Requisitos**. Cada épico agrupa os
requisitos funcionais ([RF](../requisitos/funcionais.md)) e não funcionais
([RNF](../requisitos/nao-funcionais.md)) que o realizam. Esta documentação é a
**referência**; o acompanhamento diário fica no **GitHub Projects**.

## Temas

| Tema | Objetivo | Épicos |
| --- | --- | --- |
| **T1 · Experiência Vera** | Chat, persona e explicações que fortalecem o pensamento crítico | E1, E2, E7, E11 |
| **T2 · Motor de veracidade** | Classificar notícias com custo escalonado | E3, E4, E5, E6 |
| **T3 · Canais** | Levar a Vera para onde a notícia aparece | E8, E9 |
| **T4 · Dados e qualidade** | Datasets, métricas e calibração dos pesos | E10 |

## Convenções

| Item | Padrão | Exemplo |
| --- | --- | --- |
| Tema | `T<n>` | T2 |
| Épico | `E<n>` | E4 |
| Requisito funcional | `RF-<nn>` | RF-13 |
| Requisito não funcional | `RNF-<nn>` | RNF-04 |
| Regra de negócio | `RN-<nn>` | RN-01 |
| Risco | `R-<nn>` | R-03 |

## Personas de usuário

| Persona | Descrição | Canal principal |
| --- | --- | --- |
| **Dona Célia, 67** | Recebe muitas notícias no WhatsApp e repassa para a família | Celular |
| **Lucas, 22** | Universitário, lê notícias pelo navegador e redes sociais | Extensão |
| **Ana, 35** | Professora, quer ensinar os alunos a checar informações | Site |
| **Equipe Vera** | Grupo 4: mantém a base de fontes e calibra os pesos | Painel/API |

## Definition of Ready e Definition of Done

Os critérios que um requisito precisa cumprir para entrar em uma Sprint e para ser
considerado pronto estão em [DoR e DoD](dor-dod.md).

## Páginas do backlog

- [Épicos](epicos.md): visão de cada épico, requisitos e dependências
- [MVP](mvp.md): recorte proposto para a entrega
- [Planning Poker](planning-poker.md): processo e planilha de estimativa e priorização
- [DoR e DoD](dor-dod.md): critérios de entrada e de conclusão
