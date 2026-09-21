# Requisitos funcionais

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |
    | 21/09 | 1.1 | Renumeração dos RF sem lacunas e remoção da coluna de histórias | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |
    | 21/09 | 1.2 | Revisão de granularidade: duplicatas removidas, funções do pipeline explicitadas e sujeito padronizado | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

**Legenda**

- **Canal:** :material-web: Site · :material-puzzle: Extensão · :material-cellphone: Celular ·
  :material-api: API
- **MoSCoW (proposta do PO):** **M** *Must* · **S** *Should* · **C** *Could* · **W** *Won't (agora)*.
  A proposta é revisada na priorização (ver [Planning Poker](../backlog/planning-poker.md))

!!! note "Convenções desta tabela"
    Todo requisito diz **o que** o sistema faz, com o sujeito padronizado em "O sistema deve".
    **Como** cada função é implementada (bibliotecas, APIs e modelos) fica em
    [Como a Vera funciona](../produto/funcionamento.md) e em
    [Hipóteses técnicas](../hipoteses.md), para que uma troca de técnica não invalide o
    requisito. Qualidades como desempenho, acessibilidade, responsividade e identidade visual
    são [requisitos não funcionais](nao-funcionais.md).

## Chat e conversa

| ID | Requisito | Canal | MoSCoW |
| --- | --- | --- | --- |
| RF-01 | O sistema deve receber um **link**, **texto** ou **afirmação** enviados pelo usuário para checagem | :material-web: :material-cellphone: | M |
| RF-02 | O sistema deve responder em **formato de chat**, em linguagem simples | :material-web: :material-cellphone: | M |
| RF-03 | O sistema deve exibir o **andamento da investigação**, indicando a etapa em execução | :material-web: :material-cellphone: | M |
| RF-04 | O sistema deve aceitar **perguntas de acompanhamento** sobre um resultado já entregue | :material-web: :material-cellphone: | S |
| RF-05 | O sistema deve apresentar a **reação da Vera correspondente à faixa de veracidade** do resultado | :material-web: :material-cellphone: :material-puzzle: | S |

## Motor de veracidade

| ID | Requisito | Canal | MoSCoW |
| --- | --- | --- | --- |
| RF-06 | O sistema deve **extrair título, texto, autor e data de publicação** a partir de uma URL | :material-api: | M |
| RF-07 | O sistema deve **executar a checagem em camadas** (N0 a N4), da mais barata para a mais cara | :material-api: | M |
| RF-08 | O sistema deve **encerrar a checagem** assim que a regra de parada for atingida | :material-api: | M |
| RF-09 | O sistema deve calcular o **score de veracidade** e a **confiança** do resultado | :material-api: | M |
| RF-10 | O sistema deve aplicar as **regras que se sobrepõem ao score** (RN-01 a RN-04) | :material-api: | M |
| RF-11 | O sistema deve **reaproveitar checagens anteriores** dentro do prazo de validade (RN-09) | :material-api: | S |
| RF-12 | O sistema deve concluir a checagem em **modo econômico**, sem a camada de LLM | :material-api: | S |
| RF-13 | O sistema deve registrar a **dificuldade da checagem**, pela camada em que ela parou | :material-api: | C |

## Reputação de fontes

| ID | Requisito | Canal | MoSCoW |
| --- | --- | --- | --- |
| RF-14 | O sistema deve **consultar a confiabilidade do veículo** que publicou a notícia | :material-api: | M |
| RF-15 | O sistema deve permitir **manter e atualizar a base curada de veículos** | :material-api: | M |
| RF-16 | O sistema deve consultar a **idade do domínio** | :material-api: | M |
| RF-17 | O sistema deve consultar **checagens já publicadas por agências** sobre a mesma alegação | :material-api: | M |
| RF-18 | O sistema deve manter o **histórico de notícias falsas confirmadas por domínio** (RN-10) | :material-api: | S |
| RF-19 | O sistema deve identificar **domínios que imitam veículos conhecidos** (RN-02) | :material-api: | C |
| RF-20 | O sistema deve **expor a reputação de veículos por uma API pública** | :material-api: | C |

## Análise de conteúdo

| ID | Requisito | Canal | MoSCoW |
| --- | --- | --- | --- |
| RF-21 | O sistema deve classificar a **probabilidade de falsidade a partir do estilo de escrita** | :material-api: | M |
| RF-22 | O sistema deve medir o **grau de sensacionalismo** do texto | :material-api: | M |
| RF-23 | O sistema deve medir a **intensidade emocional** do texto | :material-api: | M |
| RF-24 | O sistema deve verificar se o texto **cita fontes verificáveis** | :material-api: | S |
| RF-25 | O sistema deve estimar se o texto foi **gerado por IA** | :material-api: | W |
| RF-26 | O sistema deve identificar **opinião e sátira** (RN-03) | :material-api: | C |

## Corroboração

| ID | Requisito | Canal | MoSCoW |
| --- | --- | --- | --- |
| RF-27 | O sistema deve buscar **notícias semelhantes publicadas por outros veículos** | :material-api: | M |
| RF-28 | O sistema deve contar quantos **veículos confiáveis** publicaram o mesmo fato | :material-api: | M |
| RF-29 | O sistema deve **extrair do texto as alegações checáveis** | :material-api: | M |
| RF-30 | O sistema deve verificar se cada evidência **sustenta, contradiz ou é neutra** em relação à alegação | :material-api: | S |
| RF-31 | O sistema deve detectar **cópia com alteração** de outra fonte | :material-api: | C |

## Explicabilidade

| ID | Requisito | Canal | MoSCoW |
| --- | --- | --- | --- |
| RF-32 | O sistema deve apresentar **porcentagem, rótulo da faixa, principais sinais e fontes** em todo resultado (RN-05) | :material-web: :material-puzzle: :material-cellphone: | M |
| RF-33 | O sistema deve permitir consultar o **detalhamento de cada sinal e do seu peso** | :material-web: | S |
| RF-34 | O sistema deve oferecer **dicas de pensamento crítico** ligadas aos sinais encontrados | :material-web: :material-cellphone: | S |
| RF-35 | O sistema deve permitir que o usuário **conteste um resultado** | :material-web: | C |

## Extensão de navegador

| ID | Requisito | Canal | MoSCoW |
| --- | --- | --- | --- |
| RF-36 | O sistema deve checar a **notícia da aba atual** pela extensão | :material-puzzle: | S |
| RF-37 | O sistema deve exibir o **selo de reputação** do site visitado | :material-puzzle: | S |
| RF-38 | O sistema deve checar um **trecho selecionado** na página, pelo menu de contexto | :material-puzzle: | S |
| RF-39 | O sistema deve checar a **transcrição de um vídeo do YouTube**, quando houver legenda disponível | :material-puzzle: | C |

## Celular

| ID | Requisito | Canal | MoSCoW |
| --- | --- | --- | --- |
| RF-40 | O sistema deve ser **instalável como PWA** | :material-cellphone: | C |
| RF-41 | O sistema deve receber links **compartilhados de outros aplicativos** | :material-cellphone: | C |

## Histórico e últimas notícias

| ID | Requisito | Canal | MoSCoW |
| --- | --- | --- | --- |
| RF-42 | O sistema deve exibir ao usuário o **histórico das próprias consultas** | :material-web: :material-cellphone: | S |
| RF-43 | O sistema deve exibir as **últimas notícias checadas** na página inicial | :material-web: | C |

## O que saiu desta tabela

| Item | Para onde foi | Motivo |
| --- | --- | --- |
| Site responsivo a partir de 360 px | [RNF-10](nao-funcionais.md) | Era duplicata de um requisito não funcional já existente |
| Persona, frases temáticas e animações | [RNF-20](nao-funcionais.md) e [RNF-08](nao-funcionais.md) | Identidade e acessibilidade são qualidades, não funções |
| Aplicativo nativo (Android/iOS) | [MVP](../backlog/mvp.md) | É uma decisão de canal e de escopo, não um requisito |
| Técnicas citadas nos requisitos (RDAP, Fact Check API, TF-IDF, NRC, NLI) | [Como a Vera funciona](../produto/funcionamento.md) | O requisito diz o que fazer; a técnica pode mudar na fase Investigate |
