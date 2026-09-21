# Definition of Ready e Definition of Done

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 18/09 | 1.0 | Criação da página | Maykon Soares |
    | 21/09 | 1.1 | Critérios passam a valer por requisito, não por história | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

!!! warning "Proposta para validar"
    Os critérios abaixo são a **proposta inicial**. A equipe valida (e ajusta) na próxima
    Sprint Planning.

## Definition of Ready (DoR)

Um requisito só entra em uma sprint quando cumpre **todos** os itens:

- [ ] Está descrito de forma verificável na página de
      [requisitos funcionais](../requisitos/funcionais.md) ou
      [não funcionais](../requisitos/nao-funcionais.md), com ID próprio.
- [ ] Diz a quem serve: canal e persona afetada (ver [Senhora Vera](../produto/vera.md)).
- [ ] Tem uma forma objetiva de verificar se foi atendido (comportamento observável ou métrica).
- [ ] Está ligado a um [épico](epicos.md).
- [ ] Foi estimado em story points na [Planning Poker](planning-poker.md).
- [ ] Tem valor de negócio (1–5) atribuído pelo PO.
- [ ] Cabe em uma sprint (1 semana); se não couber, é quebrado antes.
- [ ] Dependências (APIs, datasets, outros requisitos) estão identificadas e disponíveis.
- [ ] Riscos associados estão no [Mapa de riscos](../riscos.md), quando houver.
- [ ] A equipe entende o requisito e não tem dúvidas abertas sobre ele.

## Definition of Done (DoD)

Um requisito só é considerado pronto quando cumpre **todos** os itens:

- [ ] O comportamento descrito no requisito foi implementado e demonstrado.
- [ ] O código está versionado no repositório e passou por revisão (Pull Request aprovado
      por pelo menos um colega).
- [ ] Testes cobrem o comportamento descrito no requisito.
- [ ] Respeita os [requisitos não funcionais](../requisitos/nao-funcionais.md) e as
      [regras de negócio](../requisitos/regras-de-negocio.md) aplicáveis.
- [ ] As respostas da Vera **explicam os critérios** usados na classificação (o usuário
      entende por que a notícia recebeu aquela veracidade).
- [ ] A documentação afetada foi atualizada neste site, com linha nova no histórico de
      revisão da página.
- [ ] Foi apresentada na Sprint Review e aceita pelo PO.
