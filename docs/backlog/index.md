# Visão geral do backlog

O Product Backlog segue a hierarquia definida na [Metodologia](../metodologia.md):
**Temas → Épicos → Histórias de usuário**. Esta documentação é a **referência**; o
acompanhamento diário fica no **GitHub Projects**.

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
| História | `US-<épico>.<n>` | US-4.2 |
| Requisito funcional | `RF-<nn>` | RF-13 |
| Requisito não funcional | `RNF-<nn>` | RNF-04 |
| Regra de negócio | `RN-<nn>` | RN-01 |
| Risco | `R-<nn>` | R-03 |

**Formato das histórias:** *Como* [persona], *quero* [ação], *para* [benefício].

**Critérios de aceite:** formato **Dado / Quando / Então** (Gherkin), para virarem testes
diretamente.

## Personas de usuário

| Persona | Descrição | Canal principal |
| --- | --- | --- |
| **Dona Célia, 67** | Recebe muitas notícias no WhatsApp e repassa para a família | Celular |
| **Lucas, 22** | Universitário, lê notícias pelo navegador e redes sociais | Extensão |
| **Ana, 35** | Professora, quer ensinar os alunos a checar informações | Site |
| **Equipe Vera** | Grupo 4: mantém a base de fontes e calibra os pesos | Painel/API |

## Definition of Ready (DoR)

Uma história **só entra na Sprint** quando:

- [ ] segue o formato *Como / quero / para*;
- [ ] tem critérios de aceite em Dado / Quando / Então;
- [ ] está ligada a pelo menos um RF ou RNF;
- [ ] as dependências estão identificadas e resolvidas ou planejadas;
- [ ] foi **estimada no Planning Poker** (story points);
- [ ] cabe em uma Sprint (≤ 13 pontos; se passar disso, quebrar);
- [ ] a equipe entende o que é "pronto" para ela.

## Definition of Done (DoD)

Uma história **só está pronta** quando:

- [ ] todos os critérios de aceite passam;
- [ ] o código foi revisado por pelo menos 1 colega (*pull request* aprovado);
- [ ] há testes automatizados cobrindo os critérios de aceite;
- [ ] os requisitos não funcionais afetados foram verificados (acessibilidade, desempenho, segurança);
- [ ] a documentação (este MkDocs) foi atualizada se mudou comportamento, peso ou regra;
- [ ] foi demonstrada e aceita pelo PO na Sprint Review.

## Páginas do backlog

- [Épicos](epicos.md): visão de cada épico, valor e dependências
- [Histórias de usuário](historias.md): histórias com critérios de aceite
- [MVP](mvp.md): recorte proposto para a entrega
- [Planning Poker](planning-poker.md): processo e planilha de estimativa e priorização
