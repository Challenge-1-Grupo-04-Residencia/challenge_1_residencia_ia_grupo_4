# Relatório Técnico: Detecção de Desinformação Híbrida (Projeto Vera)

## 1. O Processo de Preparação dos Dados e Treinamento do Modelo

A arquitetura de detecção de desinformação exige lidar com múltiplas facetas do fenômeno: desde o sensacionalismo viral em mensageiros até notícias forjadas com aparência jornalística. Para o treinamento do modelo classificador de estilo textual (Camada N2), consolidamos cinco corpora públicos padronizados em língua portuguesa (formato Parquet):
- **`fake-br` e `FakeRecogna`**: Artigos jornalísticos extensos, balanceados entre notícias verdadeiras e falsas.
- **`fakewhatsapp-br` e `faketweet-br`**: Textos curtos, carregados de anomalias sintáticas, pontuação enfática e caixa alta — fundamentais para capturar o padrão viral de redes sociais.
- **`faketrue-br`**: Notícias de veículos consolidados e desmentidos estruturados.

### Pré-processamento Crítico e Engenharia de Features
1. **Normalização Unicode e Remoção de Acentos:** Durante a Análise Exploratória de Dados (EDA), identificamos um vazamento de dados (*data leakage*) crítico: em certos datasets, textos falsos apresentavam supressão sistemática de acentuação gráfica, enquanto os legítimos estavam ortograficamente perfeitos. Sem a normalização (`strip_accents="unicode"`), qualquer classificador aprenderia a ser um "detector de acentuação" em vez de um "detector de estilo", falhando na generalização no mundo real.
2. **Amostragem Estratificada e Balanceamento:** Para evitar que corpora volumosos (como `FakeRecogna`) diluíssem o sinal característico das mensagens de WhatsApp, limitamos o teto a 12.000 amostras por base e realizamos divisão estratificada preservando as proporções de classe ($0$ = Falso, $1$ = Verdadeiro) e fonte.
3. **Vetorização Textual:** Implementamos um `TfidfVectorizer` com extração de unigramas e bigramas (`ngram_range=(1, 2)`), sublinear TF e controle de frequência documental (`min_df=3`), capturando tanto termos isolados quanto pares de palavras característicos de apelo emocional.

### Treinamento do Modelo
O modelo final foi estruturado como um `Pipeline` do Scikit-Learn composto por:
$$\text{Texto Bruto} \longrightarrow \text{TfidfVectorizer} \longrightarrow \text{Regressão Logística (com regularização } L_2 \text{ e } C=1.0\text{)}$$
A Regressão Logística foi selecionada com pesos de classe balanceados (`class_weight='balanced'`), gerando probabilidades calibradas que alimentam a equação probabilística de veracidade do sistema.

---

## 2. Critérios para a Seleção da Abordagem Adotada

### Por que não apenas LLM (Large Language Models)?
Modelos de linguagem generativos (mesmo executados localmente, como Llama 3 8B) apresentam latência proibitiva (2 a 10 segundos por inferência), alto consumo computacional de GPU e propensão a alucinações. Utilizar uma LLM para mensurar se um texto possui caixa alta agressiva ou pontuação apelativa é computacionalmente ineficiente.

### Por que não apenas Transformers Pesados (BERTimbau)?
Embora modelos baseados em BERT alcancem bom desempenho semântico, o custo de inferência (~200 ms por amostra em GPU) inviabiliza triagens instantâneas. Além disso, o TF-IDF com Regressão Logística roda em CPU em menos de 8 ms e oferece explicabilidade direta através dos coeficientes das palavras mais indicativas de farsa — requisito central do projeto.

### Por que não apenas Machine Learning Clássico?
Modelos baseados em *bag-of-words* aprendem forma, mas não checam fatos. Se uma desinformação for redigida com gramática culta e neutralidade de tom, qualquer classificador estatístico a classificará erroneamente como verdadeira.

### A Abordagem Híbrida Adotada
Dividimos a responsabilidade entre especialidades:
1. **Modelos Discriminativos Clássicos (N2):** Classificador estatístico e heurísticas rápidas medem estilo, sensacionalismo e anomalias gramaticais em tempo real (< 10 ms).
2. **Modelos Generativos / RAG para NLI (N4):** Uma LLM atua exclusivamente na tarefa de *Natural Language Inference* (NLI) sobre as evidências retornadas pela base vetorial (PGVector), respondendo se a evidência sustenta ou contradiz a alegação original.

---

## 3. Métricas de Desempenho e Análise dos Resultados

### Validação do Classificador Estilístico (N2)
Para aferir a real generalização e evitar o sobreajuste aos jargões de um único veículo, empregamos a metodologia **Leave-One-Dataset-Out (LODO)** (treino em $N-1$ datasets e validação no corpus não visto), além do teste misto estratificado (20% de teste independente).

| Cenário de Avaliação | Acurácia | Precisão | Recall | $F_1\text{-Score (Macro)}$ | AUC-ROC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`fake-br` (Isolado via LODO)** | 86.1% | 0.85 | 0.87 | **0.86** | 0.94 |
| **`fakewhatsapp-br` (LODO)** | 70.4% | 0.69 | 0.72 | **0.70** | 0.80 |
| **Conjunto de Teste Misto (Global)** | **85.2%** | **0.84** | **0.86** | **0.85** | **0.92** |

*O desempenho no conjunto global superou com folga a meta mínima estipulada para o desafio ($F_1\text{ macro} \ge 0{,}80$).*

### Comportamento do Pipeline de Inferência Integrado
Ao estressar o pipeline integrado com notícias do mundo real via script de validação automatizada, observamos métricas alinhadas à proposta ética do projeto:
- **Taxa de Inconclusivos / Abstenção (69%):** Reflete os *guardrails* de confiança mínima. Quando os sinais são fracos ou não há evidências na web, o sistema se abstém de emitir um rótulo em vez de forçar um chute arbitrário.
- **Acurácia Condicional (61%):** Desempenho nos casos em que a confiança superou o limiar de decisão.
- **Taxa de Falsos Positivos (FPR de 19%):** Mantida sob controle graças ao estado de abstenção, protegendo veículos legítimos de acusações infundadas de falsidade.

---

## 4. Principais Desafios Enfrentados

1. **O Gargalo da Meta-Checagem no NLI:** Fazer a LLM entender que uma matéria de agência intitulada *"É falso que vacinas causam autismo"* **contradiz** a alegação *"Vacinas causam autismo"*. Por compartilharem os mesmos termos, o modelo tendia a rotular como neutro ou favorável. A solução exigiu engenharia de prompt estruturada com regras explícitas de meta-checagem.
2. **Textos Curtos vs. Matrizes Esparsas:** Em corpora de redes sociais (`faketweet-br`, `fakewhatsapp-br`), o vocabulário reduzido por mensagem gerava vetores TF-IDF extremamente esparsos. A combinação de unigramas com bigramas e métricas complementares de sensacionalismo compensou essa limitação.
3. **Instabilidade de Saída em Modelos Locais (JSON Parsing):** Modelos quantizados menores (8B) frequentemente quebram esquemas estritos de saída. Foi necessário projetar parsers tolerantes a anomalias estruturais nas respostas do Ollama.

---

## 5. Aprendizados e Lições Adquiridas

1. **Engenharia de Dados Antecede a Modelagem:** A detecção do viés de acentuação na EDA reforçou que investigar os pesos dos coeficientes (*feature importance*) é pré-requisito indispensável antes de validar qualquer acurácia alta.
2. **Abordagens Híbridas Superam Soluções Unilaterais:** Unir o rigor estatístico e a velocidade do Machine Learning clássico à capacidade de raciocínio da IA Generativa produziu um sistema robusto, rápido e economicamente viável.
3. **A Ética da Abstenção na IA:** Reconhecer quando o modelo não tem dados suficientes para opinar (*Confidence Thresholding*) é a maior garantia de segurança contra desinformação e calúnia.
