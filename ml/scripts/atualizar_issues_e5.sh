#!/bin/bash

REPO="Challenge-1-Grupo-04-Residencia/challenge_1_residencia_ia_grupo_4"

echo "Atualizando a Issue #12..."
./gh issue edit 12 --repo "$REPO" --body "**História de Usuário**
Como leitor, quero que a Vera detecte se a escrita da notícia tem o estilo típico de fake news, para que eu desconfie de textos com linguagem manipulativa.

**Requisito Base:** RF-21
**Critérios de Aceitação:**
* **Dado que** uma notícia é submetida ao Motor de Veracidade,
* **Quando** passar pela Camada N2,
* **Então** o sistema deve aplicar um classificador (Regressão Logística/TF-IDF) para extrair o estilo de escrita.
* **E** o sistema deve devolver a probabilidade (de 0 a 1) do texto usar táticas linguísticas de desinformação.
* **E** a checagem não deve falhar se o texto for muito curto (< 10 palavras)."

echo "Atualizando a Issue #13..."
./gh issue edit 13 --repo "$REPO" --body "**História de Usuário**
Como leitor, quero ser alertado se o texto apela ao sensacionalismo (uso exagerado de maiúsculas, exclamações e urgência), para não cair em \"caça-cliques\".

**Requisito Base:** RF-22
**Critérios de Aceitação:**
* **Dado que** o texto foi carregado para a análise de conteúdo,
* **Quando** as métricas heurísticas forem computadas,
* **Então** o sistema deve contabilizar a proporção de letras em CAIXA ALTA, pontuação expressiva (!!!) e gatilhos de alerta.
* **E** essas contagens devem gerar um sub-score de sensacionalismo."

echo "Atualizando a Issue #14..."
./gh issue edit 14 --repo "$REPO" --body "**História de Usuário**
Como leitor, quero entender se a notícia está usando emoções fortes (raiva, urgência, medo) para tentar direcionar minha opinião e me manipular.

**Requisito Base:** RF-23
**Critérios de Aceitação:**
* **Dado que** a notícia está sob escrutínio da Camada N2,
* **Quando** o processamento de texto for executado,
* **Então** o sistema deve utilizar um mapeamento léxico (ex: NRC Emotion) para mensurar emoções predominantes.
* **E** registrar a carga (ex: raiva/nojo) no relatório de explicabilidade."

echo "Atualizando a Issue #15..."
./gh issue edit 15 --repo "$REPO" --body "**História de Usuário**
Como um leitor crítico, quero saber se o texto cita abertamente alguma fonte rastreável ou se tira afirmações \"do nada\", para me ajudar a avaliar sua credibilidade.

**Requisito Base:** RF-24
**Critérios de Aceitação:**
* **Dado que** o texto está sendo avaliado pelo pipeline,
* **Quando** o motor processar as sentenças,
* **Então** deve identificar a presença de URLs incorporadas ou menções diretas de autoridades.
* **E** caso cite fontes explicitamente, o score de estilo deve receber um incremento positivo."

echo "Atualizando a Issue #16..."
./gh issue edit 16 --repo "$REPO" --body "**História de Usuário**
Como leitor ocasional, quero ser avisado caso um texto seja opinativo ou de um portal de humor (sátira), para que eu não espere fatos concretos de onde não existe jornalismo factual.

**Requisito Base:** RF-26
**Critérios de Aceitação:**
* **Dado que** a notícia vem de um domínio analisado,
* **Quando** o site estiver listado como portal de humor ou a gramática for de artigo de opinião (1ª pessoa),
* **Então** o fluxo deve rotular a notícia com a tag especial \"Sátira/Opinião\".
* **E** informar isso diretamente no chat sem penalizar a nota principal."

echo "Concluído! Issues #12 a #16 foram formatadas com INVEST/BDD."
