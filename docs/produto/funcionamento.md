# Como a Vera funciona

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |
    | 21/09 | 1.1 | Remoção das histórias de usuário e ajuste das referências | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

!!! danger "Proposta para validar"
    A arquitetura abaixo é a **proposta inicial** do grupo. Os limiares e as camadas
    precisam ser validados com dados na fase Investigate.

## Princípio: escalonar o custo

Nem toda notícia precisa de uma LLM. Uma notícia de um site criado há três dias, que
nenhum veículo publicou e que já foi desmentida por uma agência de checagem, é resolvida
**sem IA generativa**.

A Vera verifica em **camadas** que vão da mais barata para a mais cara. Depois de cada
camada ela calcula a veracidade e a **confiança** no resultado. Se a confiança já for
suficiente, ela **para e responde**. Se não for, sobe para a próxima camada.

```mermaid
flowchart TD
    E([Pergunta: link, texto ou afirmação]) --> N0
    N0["<b>N0 · Cache</b><br/>já foi checada?"] -->|sim| R
    N0 -->|não| N1
    N1["<b>N1 · Fonte</b><br/>reputação, idade do domínio,<br/>checagens existentes"] --> D1{confiança<br/>suficiente?}
    D1 -->|sim| R
    D1 -->|não| N2
    N2["<b>N2 · Conteúdo</b><br/>ML clássico, estilo,<br/>emoção"] --> D2{confiança<br/>suficiente?}
    D2 -->|sim| R
    D2 -->|não| N3
    N3["<b>N3 · Corroboração</b><br/>busca de notícias semelhantes<br/>e similaridade"] --> D3{confiança<br/>suficiente?}
    D3 -->|sim| R
    D3 -->|não| N4
    N4["<b>N4 · LLM</b><br/>extrai alegações, NLI<br/>contra evidências"] --> R
    R([Vera responde: veracidade + motivos + fontes])
```

## Camadas

| Camada | O que faz | Técnica | Custo | Latência alvo |
| --- | --- | --- | --- | --- |
| **N0 · Cache** | Reaproveita checagens já feitas da mesma URL ou afirmação | Hash da URL normalizada, similaridade de texto | Nenhum | < 200 ms |
| **N1 · Fonte** | Avalia **quem** publicou | Base de fontes curada, RDAP/WHOIS, Google Fact Check Tools API, histórico de fakes do domínio | Muito baixo (consulta a APIs) | < 2 s |
| **N2 · Conteúdo** | Avalia **como** está escrito | TF-IDF + SVM / Regressão Logística / Random Forest, heurísticas de estilo, NRC Emotion Lexicon | Baixo (CPU) | < 1 s |
| **N3 · Corroboração** | Verifica se **outros** publicaram o mesmo | Busca de notícias (GDELT, API de busca, RSS de veículos), *embeddings* para similaridade | Médio | < 8 s |
| **N4 · LLM** | Resume, extrai alegações e confere contra as evidências | LLM + NLI (sustenta / contradiz / neutro) | Alto (tokens) | < 20 s |

## Dificuldade da notícia

A camada em que a Vera parou define a **dificuldade** da checagem. O dado é útil para
métricas de custo e para calibrar os limiares:

| Dificuldade | Resolvida em | Exemplo |
| --- | --- | --- |
| :material-circle:{ style="color: #2e7d32" } **Fácil** | N0 ou N1 | Já desmentida por uma agência; site criado há uma semana |
| :material-circle:{ style="color: #f9a825" } **Mediano** | N2 ou N3 | Texto sensacionalista que nenhum veículo confiável replicou |
| :material-circle:{ style="color: #c62828" } **Difícil** | N4 | Notícia plausível, bem escrita, com meia-verdade ou contexto distorcido |

## Regra de parada

Depois de cada camada:

1. calcular o **score de veracidade** `V` (0 a 100) com os sinais disponíveis até ali (ver
   [Classificação](classificacao.md#formula));
2. calcular a **confiança** `C` (0 a 1): quanto do peso total já foi observado e se os
   sinais concordam entre si;
3. **parar** se `C ≥ C_min` **e** `V` estiver fora da zona de dúvida (`V ≤ 25` ou `V ≥ 75`);
4. **parar sempre** se existir checagem de agência signatária da IFCN (regra
   [RN-01](../requisitos/regras-de-negocio.md));
5. caso contrário, subir de camada.

!!! tip "Valores iniciais sugeridos"
    `C_min = 0,7`. A zona de dúvida (26 a 74) deve ser recalibrada com o dataset de
    avaliação (RNF-07).

## Modelo de baixo custo × alto custo

O brainstorm pediu dois modelos. Na arquitetura em camadas eles viram **modos de operação**
do mesmo pipeline:

| | Modo econômico | Modo completo |
| --- | --- | --- |
| Camadas | N0 a N3 | N0 a N4 |
| Usa LLM | Não | Só quando as camadas anteriores não bastam |
| Explicação | Montada por *templates* com as frases da Vera | Gerada pela LLM na voz da Vera, com as evidências |
| Uso previsto | Extensão (selo do site), plano gratuito, fallback se a LLM cair | Chat, notícias difíceis |

## Arquitetura de alto nível

```mermaid
flowchart LR
    subgraph Canais
        W[Site / PWA]
        X[Extensão]
    end
    W & X --> API[API Vera]
    API --> P[Orquestrador de camadas]
    P --> F[(Base de fontes<br/>e histórico)]
    P --> EXT[APIs externas<br/>Fact Check · RDAP · busca]
    P --> ML[Modelos N2]
    P --> LLM[Provedor de LLM]
    API --> API2[API de reputação<br/>de veículos]
    API2 --> F
```

A **API de reputação de veículos** é um produto em si: responde "este domínio é
confiável?" e serve à extensão (selo), ao chat e, no futuro, a terceiros.

## Limitações e Oportunidades de Melhoria (Débitos Técnicos)

Apesar da arquitetura em camadas ser escalável, o MVP atual possui algumas limitações técnicas conhecidas que representam oportunidades de evolução (Backlog Futuro):

### 1. Bloqueios de Web Scraping em Fontes Oficiais
A camada `LeitorLink` tenta extrair o texto de URLs fornecidas, mas encontra barreiras severas (Erro 403 / Cloudflare) ao tentar acessar sites governamentais (como `tse.jus.br`) ou veículos de imprensa com *paywall* agressivo.
* **Impacto:** O texto fica inacessível para a camada de Estilo (N2), o que reduz as evidências processadas e joga a pontuação para a faixa de "Inconclusivo".
* **Melhoria Futura:** Integrar serviços especializados em bypass de anti-bot ou implementar Puppeteer/Playwright *headless* para conseguir extrair conteúdos de fontes VIP com segurança e estabilidade, além de exibir mensagens na tela informando ativamente o usuário sobre o bloqueio.

### 2. Gargalo de Meta-Checagem no RAG
Atualmente, se uma fake news é muito difundida, a Busca Semântica (N3) retorna artigos desmentindo essa notícia (ex: *"Como a teoria falsa de que Lula morreu..."*). O desafio é que o classificador de desmentidos atual (`e_checagem_desta_alegacao`) usa heurísticas textuais e pode falhar em marcar essas matérias como uma *Checagem Oficial* para acionar a Regra de Negócio soberana (RN-01).
* **Solução Tática Adotada no MVP:** Calibramos o *Prompt* da camada N4 (LLM Llama 3) com foco em *Natural Language Inference* (NLI) para induzi-la a deduzir que matérias sobre "boatos" são, por tabela, refutações da alegação principal. Isso evita falsos inconclusivos, mas atua como um "band-aid" de Engenharia de Prompt.
* **Solução Estrutural Ideal (Futura):** Implementar um modelo classificador *Cross-Encoder* dedicado, super leve, que identifique rapidamente se "Texto A é um desmentido de Texto B". Caso positivo, a N3 assumirá o protagonismo e abortará o pipeline via RN-01, sem gastar tokens, latência ou correr o risco de alucinação na camada generativa (N4).
