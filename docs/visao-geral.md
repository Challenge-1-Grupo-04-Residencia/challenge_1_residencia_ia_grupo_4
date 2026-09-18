# Challenge 1 — Fake News e Desinformação

Documentação do **Grupo 4** da Residência em IA. O projeto segue o framework
**Challenge Based Learning (CBL)** e usa **Scrum adaptado** para a execução.

!!! abstract "A Grande Ideia"
    Em um mundo com excesso de informação, como distinguir fatos, evidências e opiniões?
    A IA pode apoiar a investigação da confiabilidade das informações, **fortalecendo o
    pensamento crítico em vez de substituí-lo**.

!!! quote "O produto: Senhora Vera"
    **"O que você quer saber que é verdade?"** Uma senhora fofoqueira que sabe de tudo, mas
    só acredita depois de conferir as fontes. Disponível como site, extensão de navegador e
    no celular. [Conheça a Vera →](produto/vera.md)

## Equipe

| Membro | Papel |
| --- | --- |
| Maykon Soares | Product Owner · Developer |
| Ian Costa | Scrum Master · Developer |
| Luísa Brambilla | Developer |
| Natália Evelin | Developer |
| Rebeca Bontempo | Developer |

## Onde estamos

- [x] **Semana 1 — Engage**: Big Idea, Essential Question e Challenge definidos (07/09 a 11/09)
- [x] **Semana 2 — Backlog**: produto, requisitos, classificação, riscos e backlog documentados
- [ ] **Semanas 2 e 3 — Investigate**: pesquisa de artigos e fontes, respostas às Guiding Questions
- [ ] **Semanas 4 e 5 — Act**: desenvolvimento do protótipo

## Por onde começar

<div class="grid cards" markdown>

-   :material-target: **[O Desafio](desafio.md)**

    Big Idea, Essential Question, Challenge e as Guiding Questions.

-   :material-account-voice: **[Senhora Vera](produto/vera.md)**

    Visão do produto, persona, canais e identidade visual.

-   :material-layers-triple: **[Como a Vera funciona](produto/funcionamento.md)**

    Pipeline em camadas: do mais barato até a LLM.

-   :material-scale-balance: **[Classificação e pesos](produto/classificacao.md)**

    Sinais, pesos, fórmula e faixas de veracidade.

-   :material-clipboard-list: **[Requisitos](requisitos/funcionais.md)**

    Funcionais, não funcionais e regras de negócio.

-   :material-view-column: **[Backlog](backlog/index.md)**

    Épicos, histórias com critérios de aceite, MVP e Planning Poker.

-   :material-alert: **[Mapa de riscos](riscos.md)**

    Probabilidade × impacto e mitigação.

-   :material-magnify: **[Investigação](investigacao.md)**

    Estudos de caso, datasets públicos e APIs.

</div>

## Rodando esta documentação

```bash
uv run mkdocs serve   # http://127.0.0.1:8000
uv run mkdocs build   # gera o site estático em site/
```
