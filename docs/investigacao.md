# Investigação

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

!!! warning "Verificar antes de usar"
    A lista é o ponto de partida da pesquisa. Tamanho, licença e disponibilidade de cada
    dataset precisam ser **conferidos na fonte original** e registrados aqui.

| Dataset | Idioma | Conteúdo | Uso previsto | Tamanho | Licença | Limitações |
| --- | --- | --- | --- | --- | --- | --- |
| **Fake.Br Corpus** | PT-BR | Notícias falsas e verdadeiras pareadas por tema | Treino/teste do N2 (principal) | | | |
| **FakeRecogna** | PT-BR | Notícias falsas e verdadeiras | Teste com notícias mais recentes | | | |
| **FACTCK.BR** | PT-BR | Alegações checadas por agências brasileiras | Avaliação de N1 (RN-01) e N4 | | | |
| **LIAR** | EN | Declarações do PolitiFact com 6 rótulos | Referência de literatura | | | |
| **FakeNewsNet** | EN | Notícias + contexto social | Referência de literatura | | | |

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

- [ ] Existe uma API de credibilidade de veículos brasileiros, ou precisamos **construir** a nossa (US-4.1, US-4.6)?
- [ ] Como tratar fontes que são **artigos científicos** (revisão por pares, metodologia, base de publicação)?
- [ ] Se a fonte citada é um website, ela também passa pela checagem completa? Até que profundidade?
- [ ] Viés político do veículo deve **mesmo** ficar fora do score (RN-08)?
- [ ] Qual o limiar de "site novo" que melhor separa fake de verdadeira nos dados?
- [ ] Qual provedor e modelo de LLM usar no N4 (custo × qualidade em PT-BR)?
- [ ] Fine-tuning de um modelo em PT-BR compensa frente a TF-IDF + modelo clássico?

## Registro de descobertas

| Data | Quem | Descoberta | Impacto (peso, regra, requisito) |
| --- | --- | --- | --- |
| | | | |
