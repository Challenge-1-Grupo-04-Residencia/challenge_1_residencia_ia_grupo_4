# Requisitos funcionais

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |

**Legenda**

- **Canal:** :material-web: Site · :material-puzzle: Extensão · :material-cellphone: Celular ·
  :material-api: API
- **MoSCoW (proposta do PO):** **M** *Must* · **S** *Should* · **C** *Could* · **W** *Won't (agora)*.
  A proposta é revisada na priorização (ver [Planning Poker](../backlog/planning-poker.md))
- **História:** onde estão os critérios de aceite no [backlog](../backlog/historias.md)

## Chat e persona

| ID | Requisito | Canal | MoSCoW | História |
| --- | --- | --- | --- | --- |
| RF-01 | O usuário envia um **link**, **texto** ou **afirmação** para a Vera checar | :material-web: :material-cellphone: | M | US-1.1 |
| RF-02 | A Vera responde em formato de **chat**, com a persona e as frases temáticas | :material-web: :material-cellphone: | M | US-1.2 |
| RF-03 | A Vera mostra o **estado da investigação** em tempo real (qual camada está rodando) com animação | :material-web: :material-cellphone: | S | US-1.3 |
| RF-04 | A Vera muda de **humor/animação** conforme a faixa de veracidade | :material-web: :material-cellphone: :material-puzzle: | S | US-2.2 |
| RF-05 | A Vera responde perguntas de acompanhamento sobre a checagem ("por que esse site é ruim?") | :material-web: | C | US-1.4 |

## Motor de veracidade

| ID | Requisito | Canal | MoSCoW | História |
| --- | --- | --- | --- | --- |
| RF-06 | O sistema processa a checagem em **camadas N0 a N4** com regra de parada | :material-api: | M | US-3.1 |
| RF-07 | O sistema extrai título, texto, autor e data de uma URL (*scraping*) | :material-api: | M | US-3.2 |
| RF-08 | O sistema calcula **score de veracidade** e **confiança** conforme a [fórmula](../produto/classificacao.md#formula) | :material-api: | M | US-3.3 |
| RF-09 | O sistema aplica as regras que sobrepõem o score (RN-01 a RN-04) | :material-api: | M | US-3.4 |
| RF-10 | O sistema guarda checagens em **cache** (N0) | :material-api: | S | US-3.5 |
| RF-11 | O sistema permite operar em **modo econômico** (sem LLM) | :material-api: | S | US-3.6 |

## Reputação de fontes

| ID | Requisito | Canal | MoSCoW | História |
| --- | --- | --- | --- | --- |
| RF-12 | O sistema mantém uma **base curada de veículos** com classificação de confiabilidade | :material-api: | M | US-4.1 |
| RF-13 | O sistema consulta a **idade do domínio** (RDAP/WHOIS) | :material-api: | M | US-4.2 |
| RF-14 | O sistema consulta **checagens existentes** (Google Fact Check Tools API) | :material-api: | M | US-4.3 |
| RF-15 | O sistema mantém o **histórico de fakes por domínio** | :material-api: | S | US-4.4 |
| RF-16 | O sistema detecta **domínios impostores** (RN-02) | :material-api: | C | US-4.5 |
| RF-17 | O sistema expõe uma **API pública de reputação de veículos** | :material-api: | S | US-4.6 |

## Análise de conteúdo

| ID | Requisito | Canal | MoSCoW | História |
| --- | --- | --- | --- | --- |
| RF-18 | O sistema classifica o estilo do texto com **modelo clássico** (TF-IDF + SVM/RL/RF) | :material-api: | M | US-5.1 |
| RF-19 | O sistema mede **sensacionalismo** (caixa alta, exclamações, *clickbait*) | :material-api: | S | US-5.2 |
| RF-20 | O sistema mede **intensidade emocional** (NRC Emotion Lexicon) | :material-api: | S | US-5.3 |
| RF-21 | O sistema verifica se o texto **cita fontes verificáveis** | :material-api: | C | US-5.4 |
| RF-22 | O sistema estima se o texto foi **gerado por IA** | :material-api: | W | US-5.5 |
| RF-23 | O sistema identifica **opinião e sátira** (RN-03) | :material-api: | C | US-5.6 |

## Corroboração

| ID | Requisito | Canal | MoSCoW | História |
| --- | --- | --- | --- | --- |
| RF-24 | O sistema busca **notícias semelhantes** em outros sites | :material-api: | M | US-6.1 |
| RF-25 | O sistema conta quantos **veículos confiáveis** publicaram o mesmo fato | :material-api: | M | US-6.2 |
| RF-26 | O sistema usa **LLM** para resumir a notícia e extrair alegações checáveis | :material-api: | S | US-6.3 |
| RF-27 | O sistema aplica **NLI** para saber se as evidências sustentam ou contradizem cada alegação | :material-api: | S | US-6.4 |
| RF-28 | O sistema detecta **cópia com alteração** de outra fonte (plágio) | :material-api: | C | US-6.5 |

## Explicabilidade

| ID | Requisito | Canal | MoSCoW | História |
| --- | --- | --- | --- | --- |
| RF-29 | O resultado mostra **porcentagem, faixa, sinais principais e fontes** (RN-05) | :material-web: :material-puzzle: :material-cellphone: | M | US-7.1 |
| RF-30 | O usuário vê o **detalhamento de cada sinal** e seu peso | :material-web: | S | US-7.2 |
| RF-31 | A Vera dá **dicas de pensamento crítico** ligadas aos sinais encontrados | :material-web: :material-cellphone: | S | US-7.3 |
| RF-32 | O usuário **contesta** um resultado ("acho que a Vera errou") | :material-web: | C | US-7.4 |

## Extensão de navegador

| ID | Requisito | Canal | MoSCoW | História |
| --- | --- | --- | --- | --- |
| RF-33 | A extensão checa a **notícia da aba atual** | :material-puzzle: | S | US-8.1 |
| RF-34 | A extensão exibe o **selo de reputação** do site visitado | :material-puzzle: | S | US-8.2 |
| RF-35 | A extensão checa um **trecho selecionado** pelo menu de contexto | :material-puzzle: | C | US-8.3 |

## Celular

| ID | Requisito | Canal | MoSCoW | História |
| --- | --- | --- | --- | --- |
| RF-36 | O site é **responsivo** e utilizável em telas a partir de 360 px | :material-cellphone: | M | US-9.1 |
| RF-37 | O site é **instalável** como PWA | :material-cellphone: | C | US-9.2 |
| RF-38 | O usuário **compartilha** um link de outro app direto para a Vera | :material-cellphone: | C | US-9.3 |
| RF-39 | Aplicativo **nativo** (Android/iOS) | :material-cellphone: | W | — |

## Histórico e últimas notícias

| ID | Requisito | Canal | MoSCoW | História |
| --- | --- | --- | --- | --- |
| RF-40 | O usuário vê o **histórico** das próprias consultas | :material-web: :material-cellphone: | S | US-11.1 |
| RF-41 | A página inicial mostra as **últimas notícias checadas** pela Vera | :material-web: | C | US-11.2 |
