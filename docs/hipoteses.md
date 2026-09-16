# Hipóteses técnicas

!!! danger "Nada aqui é decisão fechada"
    Pelo framework do CBL, soluções baseadas em evidências só devem ser desenvolvidas na
    fase **Act**, após pesquisa profunda. O conteúdo desta página é **brainstorming** da
    fase Engage e precisa ser validado na fase Investigate.

## Hipótese 1 — Sistemas agênticos e LLMs

A ideia é que o protótipo use um **motor multiagente** em vez de um LLM passivo. A avaliar:

- auditorias forenses — **WHOIS** (procedência de domínio), **C2PA** (proveniência de mídia);
- cruzamento de dados com **RAG** (Retrieval-Augmented Generation);
- verificação de afirmações com **NLI** (Natural Language Inference), para checar se uma
  evidência recuperada de fato sustenta ou contradiz a alegação.

Um motor multiagente combina com o requisito de transparência do Challenge: cada etapa da
verificação deixa um rastro auditável, em vez de uma resposta única sem justificativa.

## Hipótese 2 — Análise emocional

Investigar o **NRC Emotion Intensity Lexicon** para calcular picos emocionais em textos
(medo, raiva) e identificar táticas de manipulação.

A hipótese se apoia na literatura de *emotional consistency* para detecção de fake news
(ver [Referências](referencias.md)): a intensidade e a coerência emocional de um texto
carregam sinal independente do conteúdo factual.

## O que precisa ser validado na fase Investigate

- [ ] Um motor multiagente entrega ganho real sobre um LLM único, ou só adiciona custo e latência?
- [ ] WHOIS e C2PA têm cobertura suficiente no tipo de conteúdo que queremos analisar?
- [ ] Sinal emocional se sustenta em português, ou o léxico é enviesado para o inglês?
- [ ] Que baselines existem para comparar, e quais datasets públicos são utilizáveis?
