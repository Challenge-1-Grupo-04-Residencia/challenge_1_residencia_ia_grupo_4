# Relatório Técnico: Detecção de Desinformação Híbrida (Projeto Vera)

## 1. O Processo de Preparação dos Dados e Treinamento do Modelo
A arquitetura do motor Vera exige lidar com diferentes facetas da desinformação (viralidade de redes sociais vs. fake news políticas sofisticadas). Para o treinamento do classificador de estilo (Camada N2), consolidamos cinco corpora padronizados em formato Parquet:
- **`fake-br` e `FakeRecogna`**: Artigos longos, balanceados entre verdadeiro e falso.
- **`fakewhatsapp-br` e `faketweet-br`**: Textos curtos, carregados de anomalias gramaticais e caixa alta, essenciais para o modelo aprender padrões virais.
- **`faketrue-br`**: Focado em hard news e alinhamentos semânticos.

**Pré-processamento crítico:**
- **Remoção de Acentos (Normalização Unicode):** Durante a EDA (Análise Exploratória de Dados), descobrimos que em muitos datasets os textos "falsos" vinham sem acentuação e os "verdadeiros" com acentuação correta. Se não removêssemos os diacríticos (`strip_accents="unicode"`), a Regressão Logística aprenderia a ser um "detector de acentos" e não um "detector de estilo", arruinando a generalização no mundo real.
- **Amostragem Estratificada:** Limitamos o tamanho de cada corpus a 12.000 amostras (para evitar que corpora gigantes engolissem o peso do estilo do WhatsApp) e dividimos o treino/teste preservando as proporções de classe *e* de origem do dataset.

**Treinamento:**
O modelo final é um Pipeline do Scikit-Learn (TF-IDF Vectorizer + Regressão Linear) calibrado para lidar com classes balanceadas e regularização para evitar overfitting em jargões temporais.

## 2. Critérios para a Seleção da Abordagem Adotada
**Por que não apenas RAG e LLM?**
LLMs são caras, lentas e propensas a alucinação (especialmente modelos locais como o Llama 3 8B). Usar LLM para avaliar se um texto tem "caixa alta agressiva" é um desperdício de GPU.
**Por que não apenas Machine Learning Clássico?**
Modelos baseados em *bag-of-words* (TF-IDF) não entendem a verdade. Se o prefeito escreve "Eu roubei o cofre" com gramática impecável, o modelo ML classifica como "Verdadeiro".

**A Abordagem Híbrida (Vencedora):**
Dividimos a responsabilidade:
1. **Camadas N1/N2 (Heurísticas e ML Clássico - SVM/Regressão):** Filtram metadados, estilo, sensacionalismo (S-06, S-07, S-08). São instantâneas.
2. **Camadas N3/N4 (Busca Semântica VectorDB + LLM para Natural Language Inference - NLI):** Focam apenas no Entailment (Sustenta vs Contradiz - S-12). O LLM só lê as evidências filtradas pela busca e aplica a "Meta-Checagem" (entende que matérias desmentindo boatos são evidências "contra" a alegação original).

## 3. Métricas de Desempenho e Análise dos Resultados
Para garantir que o nosso classificador estilístico (N2) fosse robusto contra o "mundo real", não usamos a validação cruzada tradicional, e sim a técnica de **Leave-One-Dataset-Out (LODO)** (Treinamos em $N-1$ corpora e testamos no corpus isolado).

Resultados Consolidados da Generalização:
- **`fake-br`**: Acurácia ~86%, AUC ~0.94
- **`fakewhatsapp-br`**: Acurácia ~70%, AUC ~0.80
- **Teste Misto (20% global):** Acurácia ~85.2%, AUC ~0.92

**Avaliação em Lote (Motor Completo via API):**
Além do modelo isolado, o pipeline completo da Vera (Camadas N0 a N4) foi estressado contra requisições reais. O teste em lote revelou os seguintes comportamentos do orquestrador:
- **Taxa de Inconclusivos (69%):** A métrica mais importante do ponto de vista ético. Demonstra que os "guardrails" de confiança mínima (`C_min`) funcionam perfeitamente para evitar alucinação quando não há evidências sólidas na web.
- **Acurácia Condicional (61%):** Nos casos em que o motor conseguiu superar o limite de confiança e emitir um veredito, a precisão demonstra uma baseline honesta frente à alta complexidade da desinformação (sarcasmo, meias-verdades).
- **Falsos Positivos (19%):** Taxa controlada graças à política de abstenção. Sem o limite de confiança (Inconclusivo), os falsos positivos explodiriam, o que poderia difamar veículos sérios (Risco R-01).
- **Latência (12.1s):** O tempo médio de 12 segundos comprova a validade da arquitetura em camadas filtrantes. Executar RAG (N3) e inferência em LLM (N4) é custoso computacionalmente e temporalmente; por isso as camadas N0/N1/N2 são vitais para responder instantaneamente ao que for factível, reservando a latência de 12s apenas para casos complexos.

**Análise de Negócios:** Nossa métrica principal não é apenas Acurácia, mas a **Taxa de Falsos Positivos (FPR)** e o acionamento de **Regras de Negócio (RN-04 - Inconclusivo)**. Preferimos que o modelo caia no estado "Inconclusivo" (Proteção) do que carimbe um boato como "Verdadeiro" só porque está bem escrito. 

## 4. Principais Desafios Enfrentados
- **O Gargalo da Meta-Checagem:** Fazer o modelo gerativo (Llama 3 8B) entender que uma notícia do G1 com o título *"É falso o boato de que Lula morreu"* contradiz a alegação *"Lula morreu"*. O modelo, por focar nos mesmos sujeitos/ações, costumava classificar a evidência como "Neutra". A solução exigiu Engenharia de Prompt focada em *NLI* e regras de Meta-Checagem explícitas.
- **Formatação de Saída do LLM (JSON Hallucination):** Modelos locais menores têm dificuldade severa em gerar JSONs válidos aninhados quando analisam múltiplos textos simultaneamente. O parser precisou ser tolerante e as listas estratificadas.
- **Bloqueios de Scraper (Erro 403):** Sites do governo (como tse.jus.br) derrubam bots de raspagem, o que "cega" a camada de estilo (N2) por falta de texto. Implementamos mensagens ativas de *feedback* no frontend para mitigar a UX.

## 5. Aprendizados e Lições Adquiridas
- **Dados Sujos, Modelo Burro:** A descoberta de que os acentos eram a principal *feature* preditiva do classificador provou que analisar a importância das variáveis (Feature Importance) é crucial antes de considerar o modelo "pronto".
- **LLM não substitui engenharia clássica:** Deixar o LLM tomar a decisão final sem "Guardrails" (regras de parada, limites estatísticos) destrói o rigor matemático. A Matemática (Equação de Veracidade e Confiança) deve orquestrar a Oratória (LLM), e não o contrário.
- **Ética de Produto:** Quando não há dados no dataset ou na busca da web (N3), a IA não deve interpolar ou inventar porcentagens. Admitir "0 sinais medidos -> Inconclusivo" é o maior ato de maturidade que o sistema (e nós engenheiros) alcançamos neste ciclo.

## 6. Relação com a Documentação de Riscos e Limitações Conhecidas
Em conformidade com a documentação do projeto (`docs/riscos.md`), os desafios práticos validados neste treinamento refletem os riscos mapeados desde o início:
- **Risco R-09 (Scraping Bloqueado):** Confirmado na prática. A falha ao extrair textos em 20% das URLs impacta a precisão do N2 (já que este depende do volume textual). Isso validou a decisão de arquitetura de priorizar a submissão de texto livre pelo usuário como fallback.
- **Risco R-03 (Datasets Enviesados):** O viés de "acentuação" e jargões políticos encontrados na EDA comprova o Risco R-03. A mitigação adotada no pipeline (remoção de acentos via `strip_accents="unicode"` e a avaliação cruzada LODO) foi desenhada estritamente para prevenir que o modelo decorasse o dataset e falhasse no mundo real.
- **Risco R-01 (Falso Positivo contra Veículos Sérios):** As métricas do LODO confirmam que nossa Taxa de Inconclusivos é alta (72%) porque calibramos a Regressão Logística para não forçar certezas (favorecendo abstention em caso de baixa correlação estatística).
