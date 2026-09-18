# Definition of Ready e Definition of Done

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 18/09 | 1.0 | Criação da página | Maykon Soares |

!!! warning "Proposta para validar"
    Os critérios abaixo são a **proposta inicial**. A equipe valida (e ajusta) na próxima
    Sprint Planning.

## Definition of Ready (DoR)

Uma história só entra em uma sprint quando cumpre **todos** os itens:

- [ ] Está escrita no formato *Como [persona], quero [ação], para [benefício]*, com uma das
      personas definidas em [Senhora Vera](../produto/vera.md).
- [ ] Está vinculada a pelo menos um [requisito funcional](../requisitos/funcionais.md) (RF).
- [ ] Tem critérios de aceite em Gherkin (*Dado / Quando / Então*), como em
      [Histórias de usuário](historias.md).
- [ ] Foi estimada em story points na [Planning Poker](planning-poker.md).
- [ ] Tem valor de negócio (1–5) atribuído pelo PO.
- [ ] Cabe em uma sprint (1 semana); se não couber, é quebrada antes.
- [ ] Dependências (APIs, datasets, outras histórias) estão identificadas e disponíveis.
- [ ] Riscos associados estão no [Mapa de riscos](../riscos.md), quando houver.
- [ ] A equipe entende a história e não tem dúvidas abertas sobre ela.

## Definition of Done (DoD)

Uma história só é considerada pronta quando cumpre **todos** os itens:

- [ ] Todos os critérios de aceite foram atendidos e demonstrados.
- [ ] O código está versionado no repositório e passou por revisão (Pull Request aprovado
      por pelo menos um colega).
- [ ] Testes cobrem o comportamento descrito nos critérios de aceite.
- [ ] Respeita os [requisitos não funcionais](../requisitos/nao-funcionais.md) e as
      [regras de negócio](../requisitos/regras-de-negocio.md) aplicáveis.
- [ ] As respostas da Vera **explicam os critérios** usados na classificação (o usuário
      entende por que a notícia recebeu aquela veracidade).
- [ ] A documentação afetada foi atualizada neste site, com linha nova no histórico de
      revisão da página.
- [ ] Foi apresentada na Sprint Review e aceita pelo PO.
