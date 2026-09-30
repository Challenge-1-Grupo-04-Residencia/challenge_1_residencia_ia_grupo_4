#!/bin/bash
REPO="Challenge-1-Grupo-04-Residencia/challenge_1_residencia_ia_grupo_4"

echo "Logando no GitHub..."
./gh auth status || { echo "Por favor, rode './gh auth login' primeiro."; exit 1; }

echo "Criando as Labels no repositório..."
# Eixo 1: Tipo
./gh label create "type: epic" --repo "$REPO" --color "6F42C1" --description "Épico que engloba várias histórias" --force
./gh label create "type: story" --repo "$REPO" --color "2EA043" --description "História de Usuário (Requisito)" --force
./gh label create "type: task" --repo "$REPO" --color "6E7681" --description "Tarefa técnica" --force
./gh label create "type: bug" --repo "$REPO" --color "D73A4A" --description "Erro ou falha a corrigir" --force

# Eixo 2: Módulo/Escopo
./gh label create "scope: N0-N1" --repo "$REPO" --color "0075ca" --description "Cache e Reputação de Fontes" --force
./gh label create "scope: N2" --repo "$REPO" --color "1d76db" --description "Estilo de Conteúdo e ML Clássico" --force
./gh label create "scope: N3-N4" --repo "$REPO" --color "008672" --description "Corroboração e LLM" --force
./gh label create "scope: api" --repo "$REPO" --color "5319e7" --description "Orquestrador e Back-end (FastAPI)" --force
./gh label create "scope: front-web" --repo "$REPO" --color "e28325" --description "Interface Web e Chat" --force
./gh label create "scope: front-ext" --repo "$REPO" --color "fbca04" --description "Extensão de Navegador" --force
./gh label create "scope: front-mobile" --repo "$REPO" --color "d93f0b" --description "PWA e Mobile" --force

# Eixo 3: Prioridade
./gh label create "priority: must" --repo "$REPO" --color "B60205" --description "Alta Prioridade (Essencial para o MVP)" --force
./gh label create "priority: should" --repo "$REPO" --color "FBCA04" --description "Média Prioridade (Importante ter)" --force
./gh label create "priority: could" --repo "$REPO" --color "0E8A16" --description "Baixa Prioridade (Desejável)" --force

echo "Labels criadas com sucesso!"

echo "Aplicando labels dinamicamente às issues por título..."

# Função para achar a issue pelo título e aplicar a label
aplicar_label() {
    local titulo="$1"
    local labels="$2"
    
    # Busca o ID numérico da issue usando o CLI do GitHub filtrando por título exato
    local issue_id=$(./gh issue list --repo "$REPO" --search "\"$titulo\" in:title" --json number --jq '.[0].number')
    
    if [ -n "$issue_id" ]; then
        echo "Aplicando [$labels] na Issue #$issue_id..."
        ./gh issue edit $issue_id --repo "$REPO" --add-label "$labels"
    else
        echo "Aviso: Issue '$titulo' não encontrada. Ignorando..."
    fi
}

# --- APLICANDO NO ÉPICO E5 (N2) ---
aplicar_label "[Épico E5] Análise de conteúdo" "type: epic,scope: N2"
aplicar_label "[US] Detecção de estilo falso" "type: story,scope: N2,priority: must"
aplicar_label "[US] Alerta de sensacionalismo" "type: story,scope: N2,priority: must"
aplicar_label "[US] Termômetro emocional do texto" "type: story,scope: N2,priority: must"
aplicar_label "[US] Verificação de citação de fontes" "type: story,scope: N2,priority: should"
aplicar_label "[US] Distinção de opinião e sátira" "type: story,scope: N2,priority: could"

# --- APLICANDO NO ÉPICO E3 (Orquestrador) ---
aplicar_label "[Épico E3] Pipeline em camadas" "type: epic,scope: api"
aplicar_label "[US] Extração de metadados da notícia" "type: story,scope: api,priority: must"
aplicar_label "[US] Orquestração e Regra de Parada" "type: story,scope: api,priority: must"
aplicar_label "[US] Score de Veracidade e Confiança" "type: story,scope: api,priority: must"

# --- APLICANDO NO ÉPICO E4 (Fontes N1) ---
aplicar_label "[Épico E4] Reputação de fontes" "type: epic,scope: N0-N1"
aplicar_label "[US] Consulta à reputação do veículo" "type: story,scope: N0-N1,priority: must"
aplicar_label "[US] Checagem preemptiva (Fact Check API)" "type: story,scope: N0-N1,priority: must"

# --- APLICANDO NOS DEMAIS ---
aplicar_label "[Épico E1] Chat com a Vera" "type: epic,scope: front-web"
aplicar_label "[US] Entrada de dados para checagem" "type: story,scope: front-web,priority: must"
aplicar_label "[US] Resposta em formato de chat" "type: story,scope: front-web,priority: must"
aplicar_label "[US] Feedback de carregamento em etapas" "type: story,scope: front-web,priority: must"
aplicar_label "[US] Perguntas de acompanhamento" "type: story,scope: front-web,priority: should"

aplicar_label "[Épico E2] Persona e identidade visual" "type: epic,scope: front-web"
aplicar_label "[US] Reação da Persona" "type: story,scope: front-web,priority: should"

aplicar_label "[Épico E6] Corroboração" "type: epic,scope: N3-N4"
aplicar_label "[US] Busca de notícias semelhantes" "type: story,scope: N3-N4,priority: must"
aplicar_label "[US] Inferência Lógica de Evidências (NLI)" "type: story,scope: N3-N4,priority: must"

aplicar_label "[Épico E7] Explicabilidade" "type: epic,scope: front-web"
aplicar_label "[US] Detalhamento do Veredito" "type: story,scope: front-web,priority: must"

aplicar_label "[Épico E8] Extensão de navegador" "type: epic,scope: front-ext"
aplicar_label "[US] Checagem de aba atual e selo de reputação" "type: story,scope: front-ext,priority: should"

aplicar_label "[Épico E9] Celular" "type: epic,scope: front-mobile"
aplicar_label "[US] Compartilhamento nativo no Celular (PWA)" "type: story,scope: front-mobile,priority: could"

aplicar_label "[Épico E10] Dados e avaliação" "type: epic,scope: N2"
aplicar_label "[US] Pipeline de Treinamento e Calibração (ML)" "type: story,scope: N2,priority: must"

aplicar_label "[Épico E11] Histórico e últimas notícias" "type: epic,scope: front-web"
aplicar_label "[US] Feed de últimas checagens" "type: story,scope: front-web,priority: could"

echo "Pronto! Todas as issues estão com as labels e cores corretas."
