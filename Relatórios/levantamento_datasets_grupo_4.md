# Levantamento de Datasets — Grupo 4

**Challenge 1: Fake News e Desinformação**  
**Produto:** Senhora Vera  
**Integrantes:** Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo  
**Data:** Setembro de 2026  

---

## 1. Contexto do Projeto: O que pretendemos construir

O Grupo 4 está desenvolvendo a **Vera**, uma solução de verificação de fatos orientada ao fortalecimento do pensamento crítico. Para garantir viabilidade financeira e baixa latência, o produto não recorre a Modelos de Linguagem Grandes (LLMs) em todas as requisições. 

A arquitetura opera em uma **esteira progressiva de cinco camadas (N0 a N4)**:
1. **N0 (Cache de Fatos):** Verifica se a alegação já foi checada por agências jornalísticas reconhecidas (resposta instantânea a custo zero).
2. **N1 (Reputação da Fonte):** Avalia a credibilidade do domínio e histórico de desinformação recorrente.
3. **N2 (Conteúdo e Estilo):** Executa modelos clássicos de Machine Learning em CPU para detectar sensacionalismo, apelo emocional e marcas estilísticas em milissegundos.
4. **N3 (Corroboração):** Realiza busca cruzada para verificar se veículos de imprensa estabelecidos cobriram o mesmo evento.
5. **N4 (LLM e Inferência Natural):** Acionada exclusivamente em casos complexos de alta ambiguidade para decomposição de alegações e raciocínio contextual.

A seleção dos datasets foi planejada diretamente para suprir as necessidades de cada uma dessas camadas, totalizando **346.813 registros em português do Brasil** já baixados, auditados e padronizados no ambiente de desenvolvimento da equipe.

---

## 2. Tabela de Datasets Selecionados com Links

Abaixo estão listadas as fontes primárias selecionadas para a construção e validação da Vera.

| Dataset | Link de Acesso | Volume Real | Papel Arquitetural no Projeto |
| :--- | :--- | :--- | :--- |
| **Fake.Br Corpus** | https://github.com/roneysco/Fake.br-Corpus | 7.200 notícias | Benchmark oficial de avaliação (RNF-06) e treino de estilo (N2). |
| **FakeRecogna** | https://huggingface.co/datasets/recogna-nlp/FakeRecogna | 11.902 notícias | Treino supervisionado de conteúdo multitemático pós-2018 (N2). |
| **FakeTrue.Br** | https://github.com/jpchav98/FakeTrue.Br | 3.582 notícias (1.791 pares) | Benchmark de corroboração e alinhamento boato vs notícia real (N3). |
| **FakenewsBR v6** | https://github.com/thiago-cg/fakenewsbr-v4 | 297.672 notícias | Calibração de métricas de sensacionalismo (N2) e catálogo de fontes (N1). |
| **FakeWhatsApp.Br** | https://github.com/cabrau/FakeWhatsApp.Br | 9.824 mensagens | Teste de estresse em mensagens curtas e linguagem informal de mensageria (N2). |
| **Central de Fatos** | https://huggingface.co/datasets/fake-news-UFG/central_de_fatos | 11.643 checagens | Base de checagens oficiais de 6 agências IFCN (N0) e histórico de domínios (N1). |
| **FACTCK.BR** | https://github.com/jghm-f/FACTCK.BR | 1.300 alegações | Cache de alegações estruturadas no padrão oficial ClaimReview (N0). |
| **MuMiN-PT e COVID19.BR** | https://huggingface.co/datasets/ju-resplande/portuguese-fact-checking | 3.391 publicações | Avaliação de quase-duplicatas e recirculação de alegações em redes sociais (N3). |
| **FakeTweet.Br** | https://github.com/prc992/FakeTweet.Br | 279 tweets | Teste exploratório de engajamento e microblogging (N2). |
| **FakeGen.BR** | https://github.com/Pedrest15/expanded_fake_news_corpus | 20 notícias | Teste cego contra desinformação sintética gerada por LLM (RF-25 / N4). |
| **FKTC (Fact-checked News)** | https://github.com/GoloMarcos/FKTC | 2.168 notícias | Teste de estresse temático em ciclo eleitoral (sob demanda). |

---

## 3. Justificativa de Uso por Função no Projeto

### A. Memória Rápida e Checagens Conhecidas (Camada N0)
* **Datasets:** `Central de Fatos` e `FACTCK.BR`.
* **Aplicação:** Permitem criar um índice vetorial leve para busca semântica imediata. Se a dúvida do usuário corresponder a uma alegação já desmentida por agências como Lupa, Aos Fatos, Boatos.org ou Estadão Verifica, a Vera encerra a checagem com resposta pronta em menos de 200 ms.

### B. Mapeamento de Credibilidade e Reputação de Fontes (Camada N1)
* **Datasets:** Metadados de `Central de Fatos` e `FakenewsBR v6`.
* **Aplicação:** O cruzamento das URLs e veículos dessas bases alimenta o catálogo estruturado de fontes da Vera, permitindo identificar veículos jornalísticos estabelecidos e mapear domínios com histórico comprovado de reincidência em boatos nos últimos 12 meses.

### C. Classificação de Estilo, Sensacionalismo e ML Clássico (Camada N2)
* **Datasets de Treino:** `Fake.Br Corpus` e `FakeRecogna`.
* **Aplicação:** O `Fake.Br` é a referência acadêmica por possuir pareamento temático (cada notícia falsa tem uma verdadeira sobre o mesmo fato), impedindo que o modelo aprenda viés de assunto em vez de estilo textual. O `FakeRecogna` estende essa cobertura para temas diversos (economia, saúde) até 2021.
* **Calibração de Atributos:** O `FakenewsBR v6` já possui contagens pré-calculadas de pontuação expressiva (`!`, `?`), reticências e taxa de caracteres em maiúsculas em quase 300 mil textos, servindo para calibrar a régua de sensacionalismo.
* **Testes de Canal:** `FakeWhatsApp.Br` e `FakeTweet.Br` servem para avaliar como o modelo se comporta quando o usuário envia textos curtos e gírias de aplicativos de mensagens.

### D. Corroboração e Detecção de Cópia Alterada (Camada N3)
* **Datasets:** `FakeTrue.Br` e `MuMiN-PT / COVID19.BR`.
* **Aplicação:** O `FakeTrue.Br` fornece pares alinhados entre a alegação enganosa e a apuração real publicada em veículos de referência (G1 e Folha de S.Paulo). É o conjunto ideal para validar os algoritmos de busca cruzada e identificação de adulteração de fatos.

### E. Avaliação de Riscos de IA Generativa (Camada N4)
* **Dataset:** `FakeGen.BR`.
* **Aplicação:** Composto por textos gerados pelo GPT-4.1-mini, serve estritamente como teste de resistência: avaliar se o sistema da Vera é capaz de sinalizar incoerências em desinformações produzidas por IA que apresentam gramática e coesão perfeitas.

---

## 4. Cuidados Metodológicos e Governança dos Dados

1. **Prevenção de Vazamento de Dados (Data Leakage):** Foi identificada a sobreposição de 7.160 registros do `Fake.Br` incorporados dentro do `FakenewsBR v6`. As partições de treino e teste foram estritamente isoladas para impedir contaminação nas métricas.
2. **Benchmark Oficial Isolado:** Para cumprir a meta do projeto de F1-macro maior ou igual a 0,80 (requisito RNF-06), uma partição de 20% do `Fake.Br` permanece intocada como conjunto cego de avaliação.
3. **Privacidade (LGPD):** Dados de mensagens públicas do `FakeWhatsApp.Br` contêm tratamento de anonimização e não serão expostos diretamente a usuários ou modelos externos.

---

## 5. Flexibilidade e Próximos Passos

Conforme premissa do Challenge, este levantamento representa o direcionamento técnico consolidado pela equipe até o momento. Ajustes na ponderação das bases e na engenharia de atributos poderão ocorrer durante a execução das Sprints de desenvolvimento.

