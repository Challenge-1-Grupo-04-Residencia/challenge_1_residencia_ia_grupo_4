#!/bin/bash

# Repositório alvo
REPO="Challenge-1-Grupo-04-Residencia/challenge_1_residencia_ia_grupo_4"

echo "Verificando se o GitHub CLI local está logado..."
./gh auth status || { echo "Por favor, rode './gh auth login' primeiro."; exit 1; }

echo "Criando Épico E5..."
E5_URL=$(./gh issue create --repo "$REPO" \
  --title "[Épico E5] Análise de conteúdo" \
  --body "Objetivo: Detectar sinais de falsidade na escrita. (Tema T2)")

E5_NUM=${E5_URL##*/}

echo "Épico E5 criado: #$E5_NUM. Criando Histórias de Usuário (sub-issues)..."

./gh issue create --repo "$REPO" \
  --title "[US] Detecção de estilo falso" \
  --body "**História de Usuário**
Como leitor, quero que a Vera detecte se a escrita da notícia tem o estilo típico de fake news, para que eu desconfie de textos com linguagem manipulativa.

**Requisito Base:** RF-21
**Critério de Aceite:**
- O sistema deve classificar a probabilidade de falsidade a partir da escrita.
**Dependência:** Faz parte do Épico #$E5_NUM"

./gh issue create --repo "$REPO" \
  --title "[US] Alerta de sensacionalismo" \
  --body "**História de Usuário**
Como leitor, quero ser alertado se o texto apela ao sensacionalismo (uso exagerado de maiúsculas, exclamações e urgência), para não cair em \"caça-cliques\".

**Requisito Base:** RF-22
**Critério de Aceite:**
- O sistema deve medir o grau de sensacionalismo do texto (ex: heurísticas ou Machine Learning).
**Dependência:** Faz parte do Épico #$E5_NUM"

./gh issue create --repo "$REPO" \
  --title "[US] Termômetro emocional do texto" \
  --body "**História de Usuário**
Como leitor, quero entender se a notícia está usando emoções fortes (raiva, urgência, medo) para tentar direcionar minha opinião e me manipular.

**Requisito Base:** RF-23
**Critério de Aceite:**
- O sistema deve medir a intensidade emocional do texto (ex: via NRC Emotion Lexicon).
**Dependência:** Faz parte do Épico #$E5_NUM"

./gh issue create --repo "$REPO" \
  --title "[US] Verificação de citação de fontes" \
  --body "**História de Usuário**
Como um leitor crítico, quero saber se o texto cita abertamente alguma fonte rastreável ou se tira as afirmações \"do nada\", para me ajudar a avaliar sua credibilidade.

**Requisito Base:** RF-24
**Critério de Aceite:**
- O sistema deve extrair e verificar se existem fontes/links citados como base no texto.
**Dependência:** Faz parte do Épico #$E5_NUM"

./gh issue create --repo "$REPO" \
  --title "[US] Distinção de opinião e sátira" \
  --body "**História de Usuário**
Como leitor ocasional, quero ser avisado caso um texto seja claramente opinativo ou um portal de humor (sátira), para que eu não espere fatos de onde não deveria existir jornalismo.

**Requisito Base:** RF-26
**Critério de Aceite:**
- O sistema deve sinalizar se a estrutura ou veículo indicam sátira ou artigo de opinião.
**Dependência:** Faz parte do Épico #$E5_NUM"

echo "Concluído! User Stories criadas no repositório $REPO."
