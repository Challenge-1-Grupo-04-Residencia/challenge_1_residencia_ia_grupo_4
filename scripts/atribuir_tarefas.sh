#!/bin/bash
REPO="Challenge-1-Grupo-04-Residencia/challenge_1_residencia_ia_grupo_4"

echo "Buscando IDs e atribuindo tarefas no GitHub..."

atribuir() {
    local titulo="$1"
    local pessoa="$2"
    
    # Busca a issue pelo título exato
    local issue_id=$(./gh issue list --repo "$REPO" --search "\"$titulo\" in:title" --json number --jq '.[0].number')
    
    if [ -n "$issue_id" ]; then
        echo "Atribuindo Issue #$issue_id ('$titulo') para @$pessoa..."
        ./gh issue edit $issue_id --repo "$REPO" --add-assignee "$pessoa"
    else
        echo "Aviso: Issue '$titulo' não encontrada. Ignorando..."
    fi
}

# --- IAN COSTA (Alta Dificuldade / Core Back-end e IA) ---
atribuir "[US] Orquestração e Regra de Parada" "iancostag"
atribuir "[US] Inferência Lógica de Evidências (NLI)" "iancostag"

# --- MAYKON JÚNIO (Alta Dificuldade / Algoritmos e Dados) ---
atribuir "[US] Score de Veracidade e Confiança" "maykonjuso"
atribuir "[US] Busca de notícias semelhantes" "maykonjuso"

# --- LUÍSA BRAMBILLA (Baixa Dependência / Front-end e Regras Simples) ---
atribuir "[US] Termômetro emocional do texto" "LuisaBrambilla"
atribuir "[US] Resposta em formato de chat" "LuisaBrambilla"

# --- NATÁLIA EVELIIN (Baixa Dependência / Extensão e UI) ---
atribuir "[US] Reação da Persona" "NatyEvelin"
atribuir "[US] Checagem de aba atual e selo de reputação" "NatyEvelin"

# --- REBECA BONTEMPO (Baixa Dependência / Celular e Heurísticas) ---
atribuir "[US] Alerta de sensacionalismo" "rebecaboncaputo"
atribuir "[US] Compartilhamento nativo no Celular (PWA)" "rebecaboncaputo"

echo "Todas as 10 tarefas foram distribuídas com sucesso!"
