# Investigação

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |
    | 21/09 | 1.1 | Remoção das histórias de usuário e ajuste das referências | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

Atividades da fase **Investigate** e o registro do que a equipe descobrir. O objetivo é
transformar as hipóteses do brainstorm em decisões baseadas em evidências antes da fase Act.

## Atividades da Semana 1

| Atividade | Objetivo | Saída esperada | Status |
| --- | --- | --- | --- |
| **Investigação Forense de Notícias** | Explorar estudos de caso reais de desinformação | 3 a 5 casos analisados com os sinais que os denunciaram | :material-progress-clock: |
| **Elaboração de Guiding Questions** | Organizar as perguntas que guiam a pesquisa | [Guiding Questions](desafio.md#guiding-questions) | :material-check: |
| **Workshop da Confiança** | Criar a matriz de confiança | [Sinais e pesos](produto/classificacao.md#sinais-e-pesos) v0.1 | :material-check: |
| **Exploração de datasets públicos** | Analisar dados sobre fake news | Tabela de datasets abaixo, preenchida | :material-progress-clock: |
| **Entregas** | Processo investigativo + Guiding Questions | Relatório da fase | :material-progress-clock: |

## Investigação forense: modelo de ficha

Use uma ficha por caso estudado:

| Campo | Preencher |
| --- | --- |
| Título / alegação | |
| Onde circulou (site, WhatsApp, rede social) | |
| Data em que circulou | |
| Quem desmentiu (agência, link) | |
| Tipo ([tipologia](produto/classificacao.md#o-que-e-fake-news-para-a-vera)) | |
| Sinais de **fonte** presentes (S-01 a S-05) | |
| Sinais de **conteúdo** presentes (S-06 a S-10) | |
| Sinais de **corroboração** presentes (S-11 a S-13) | |
| Em que camada a Vera teria resolvido? | |
| Viés cognitivo explorado | |
| Lição para o produto | |

## Datasets públicos

As bases em PT-BR já foram levantadas, baixadas e conferidas uma a uma: tamanho real,
conteúdo, licença e limitações estão em **[Datasets](datasets.md)**.

## Fontes de dados e APIs

Para responder à pergunta "quais sites têm maior credibilidade e publicam menos fake news":

| Fonte / API | Para que serve | Sinal | Pontos a investigar |
| --- | --- | --- | --- |
| **Google Fact Check Tools API** | Checagens publicadas no padrão ClaimReview | RN-01, S-02 | Cobertura em PT-BR, cota |
| **Signatários da IFCN** | Lista de agências de checagem certificadas | RN-01, S-01 | Atualização da lista |
| **Agências brasileiras** (Lupa, Aos Fatos, Comprova, Fato ou Fake, Estadão Verifica, Boatos.org) | Checagens e histórico de fakes por domínio | S-02 | Têm API ou RSS? Termos de uso |
| **RDAP / WHOIS** (incl. Registro.br) | Data de criação do domínio | S-03 | Limites de consulta, domínios com dados ocultos |
| **Tranco List** | Popularidade de domínios | Contexto | Popularidade ≠ confiabilidade |
| **GDELT** | Busca de notícias globais | S-11 | Cobertura de veículos brasileiros |
| **Wayback Machine (CDX API)** | Primeira vez que a página foi vista; alterações | Tempo no ar, S-13 | Latência |
| **NRC Emotion Intensity Lexicon** | Intensidade emocional | S-08 | Qualidade da tradução para PT |
| **NewsGuard / Media Bias Fact Check** | Classificação de veículos | S-01 (referência) | Pago/sem API oficial; cobertura BR |

## Perguntas em aberto

- [ ] Existe uma API de credibilidade de veículos brasileiros, ou precisamos **construir** a nossa (RF-14, RF-20)?
- [ ] Como tratar fontes que são **artigos científicos** (revisão por pares, metodologia, base de publicação)?
- [ ] Se a fonte citada é um website, ela também passa pela checagem completa? Até que profundidade?
- [ ] Viés político do veículo deve **mesmo** ficar fora do score (RN-08)?
- [ ] Qual o limiar de "site novo" que melhor separa fake de verdadeira nos dados?
- [ ] Qual provedor e modelo de LLM usar no N4 (custo × qualidade em PT-BR)?
- [ ] Fine-tuning de um modelo em PT-BR compensa frente a TF-IDF + modelo clássico?

## Registro de descobertas

| Data | Quem | Descoberta | Impacto (peso, regra, requisito) |
| --- | --- | --- | --- |
| 28/09 | Grupo 4 | Regressão Logística, Naive Bayes e LinearSVC superam RNF-06 (F1 > 0.80) na N2. Regressão Logística escolhida pela explicabilidade. | Valida a Camada N2 como filtro rápido (atende RF-32). |
| 28/09 | Grupo 4 | Regressão Logística detecta 96% dos fakes humanos, mas cai para 40% em textos de LLM. | N2 gera apenas "score de estilo", não o veredito. Textos sintéticos devem escalar para N3/N4. Mantém peso baixo do S-10. |
| 28/09 | Grupo 4 | Limiar de corroboração por similaridade (S-11) ideal é 0,10 (79,4% recall, 0,6% falsos positivos). | N3 usará TF-IDF para filtrar o Top-5. Ausência de corroboração aciona N4 em vez de reprovar. |
| 28/09 | Grupo 4 | 25% de redundância nos desmentidos e 11% de fakes repetidos. | Reforça a eficácia do Cache (N0) para barrar falsos conhecidos sem custo de LLM. |

## Análise e Escolha de Modelos (Camada N4 - NLI)

### O Desafio Técnico (A Tarefa NLP)
A Camada N4 atua como o juiz final do motor de veracidade. Para isso, o sistema requer a capacidade de comparar um texto de alegação (a notícia suspeita) com textos de evidência (corroborações coletadas pela N3). Na literatura científica de Processamento de Linguagem Natural (NLP), essa tarefa é classificada como **Natural Language Inference (NLI)**. 

O objetivo do NLI é receber dois textos (Premissa e Hipótese) e classificá-los em uma de três relações:
* **Entailment (Corroboração):** A evidência *confirma* que a notícia é verdadeira.
* **Contradiction (Refutação):** A evidência *desmente* a notícia.
* **Neutral (Neutro):** A evidência aborda o mesmo assunto, mas não confirma nem desmente a alegação.

### Critérios de Seleção (Trade-offs e Ferramental)
Foi avaliada a utilização de APIs comerciais baseadas em LLM Generativo (ex: OpenAI GPT-4o, Google Gemini). Embora essas APIs ofereçam facilidade de implementação, optamos por adotar um modelo **Local/Open Source Cross-Encoder** hospedado no Hugging Face.
Os motivos dessa escolha de design (*trade-offs*) são:
1. **Latência e Custos:** Evita o pagamento por tokens em alta volumetria e elimina a latência de rede.
2. **Privacidade e Execução Offline:** Permite que o motor de inferência rode isolado na própria infraestrutura do Backend.
3. **Maturidade Técnica:** Demonstra domínio das equipes sobre arquiteturas clássicas e eficientes (como BERT/DeBERTa) em contraste com a simples terceirização via prompts.

### O Modelo Escolhido: `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`
Dentre as opções disponíveis no Hub do Hugging Face, filtramos por modelos com suporte multilíngue (devido às restrições do Idioma Português em modelos nativos americanos) e que tivessem o melhor balanço entre peso computacional e *F1-Score*. 

A escolha recaiu sobre o `mDeBERTa-v3-base-mnli-xnli`. Analisando sua nomenclatura técnica:
* **m (Multilingual):** Treinado nativamente para compreender contexto em 100 idiomas, incluindo o Português do Brasil.
* **DeBERTa-v3:** Arquitetura criada pela Microsoft (*Decoding-enhanced BERT with disentangled attention*), que atualmente é considerada o estado da arte para tarefas de *Natural Language Understanding (NLU)*, superando o BERT tradicional.
* **base:** Representa o tamanho da rede neural (~500MB). Permite que a inferência da Camada N4 ocorra fluidamente em CPU/Memória RAM de servidores comuns, não exigindo investimento obrigatório em GPUs pesadas.
* **mnli-xnli:** O modelo foi alvo de *Fine-tuning* com os dois maiores datasets de inferência lógica do mercado (o Multi-Genre NLI e o Cross-Lingual NLI). Isso garante que os pesos matemáticos já estejam 100% calibrados para atuar como o "Juiz" que a Vera precisa.

### Metodologia de Validação Contínua
Nesta primeira *User Story* (Épico E6), o modelo atuará de forma nativa (Zero-Shot Cross-Lingual). Em fases posteriores do ciclo de vida do produto, recomenda-se criar um *benchmark* automatizado cruzando esse modelo com outros candidatos (ex: BERTimbau) sobre uma base proprietária de notícias falsas brasileiras para monitorar a variação de precisão e *Falso Positivo*.
