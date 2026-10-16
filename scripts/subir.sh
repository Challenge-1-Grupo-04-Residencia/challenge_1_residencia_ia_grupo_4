#!/usr/bin/env bash
#
# Sobe o ambiente de desenvolvimento da Senhora Vera: backend, frontend e,
# opcionalmente, o Ollama que a camada N4 usa.
#
#   ./scripts/subir.sh                  backend + frontend
#   ./scripts/subir.sh --com-ollama     também sobe o Ollama (camada N4 ativa)
#   ./scripts/subir.sh --so-backend     só a API, sem frontend
#   ./scripts/subir.sh --ajuda
#
# Ctrl+C derruba tudo o que este script subiu.
#
# ## Por que este script existe
#
# A auditoria de 05/10 encontrou um uvicorn e um next-server de **cinco dias
# antes** ainda no ar, os dois sem recarregamento automático, servindo código
# velho. A impressão era de que o motor estava quebrado: a API respondia com
# sinais que o código novo já media de outro jeito. Então este script, antes de
# subir qualquer coisa, confere as portas e derruba o que ficou para trás — e
# sempre sobe o backend com `--reload`.

set -euo pipefail

# Controle de trabalho ligado mesmo sem terminal interativo: com ele, cada serviço
# que subimos em segundo plano vira líder do seu próprio grupo de processos, e aí
# `kill -- -PID` derruba o serviço **e os filhos dele**. Sem isto, `uv run uvicorn`
# e `npm run dev` deixam netos vivos quando o pai morre — que é precisamente o
# servidor órfão que este script existe para evitar.
set -m

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

PORTA_BACKEND=8010   # a 8000 costuma estar ocupada pelo `mkdocs serve` da documentação
PORTA_FRONTEND=3000
DIRETORIO_DE_LOGS="$RAIZ/logs"

IMAGEM_OLLAMA="ollama/ollama:latest"
# Trocar por um modelo menor (llama3.2:3b baixa ~2 GB) encurta muito a primeira
# execução, mas o S-12 pesa 20 pontos e é o sinal mais pesado do catálogo: avalie a
# qualidade do julgamento com `backend/tests/laboratorio_n4.py` antes de trocar.
MODELO_OLLAMA="${OLLAMA_MODEL:-llama3}"

COM_OLLAMA=0
SO_BACKEND=0

# Cores só quando a saída é um terminal, para o log em arquivo não encher de escapes.
if [[ -t 1 ]]; then
  N="\033[0m"; NEGRITO="\033[1m"; VERDE="\033[32m"; AMARELO="\033[33m"; VERMELHO="\033[31m"; CINZA="\033[90m"
else
  N=""; NEGRITO=""; VERDE=""; AMARELO=""; VERMELHO=""; CINZA=""
fi

info()  { printf "${CINZA}·${N} %s\n" "$*"; }
ok()    { printf "${VERDE}✓${N} %s\n" "$*"; }
aviso() { printf "${AMARELO}!${N} %s\n" "$*"; }
erro()  { printf "${VERMELHO}✗${N} %s\n" "$*" >&2; }

ajuda() {
  sed -n '3,19p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --com-ollama) COM_OLLAMA=1 ;;
    --so-backend) SO_BACKEND=1 ;;
    --ajuda|-h|--help) ajuda ;;
    *) erro "opção desconhecida: $1"; echo "Use --ajuda."; exit 2 ;;
  esac
  shift
done

# ---------------------------------------------------------------------------
# Pré-requisitos
# ---------------------------------------------------------------------------

printf "\n${NEGRITO}Senhora Vera — subindo o ambiente${N}\n\n"

if ! command -v uv >/dev/null 2>&1; then
  erro "uv não encontrado. Instale: https://docs.astral.sh/uv/"
  exit 1
fi

# O Node desta máquina não veio do brew: foi instalado do binário oficial em
# ~/.local/node, que não está no PATH por padrão.
if ! command -v node >/dev/null 2>&1 && [[ -d "$HOME/.local/node/bin" ]]; then
  export PATH="$HOME/.local/node/bin:$PATH"
  info "Node encontrado em ~/.local/node/bin"
fi

if [[ $SO_BACKEND -eq 0 ]] && ! command -v node >/dev/null 2>&1; then
  aviso "Node não encontrado — subindo só o backend."
  SO_BACKEND=1
fi

mkdir -p "$DIRETORIO_DE_LOGS"   # já está no .gitignore

# ---------------------------------------------------------------------------
# Portas: derruba só o que é nosso
# ---------------------------------------------------------------------------

# Libera a porta derrubando **apenas** servidor de desenvolvimento deste projeto.
# Qualquer outra coisa na porta é problema de quem está na máquina, e o script para em
# vez de adivinhar de quem é o processo.
#
# O reconhecimento olha a linha de comando e também o processo pai, porque `uvicorn
# --reload` roda em dois: o pai, que casa com "uvicorn", e um filho cuja linha de
# comando é `python -c from multiprocessing...` e não casa com nada. A primeira versão
# disto matava o pai, encontrava o filho ainda segurando a porta, não o reconhecia e
# abortava a subida inteira.
liberar_porta() {
  local porta="$1" nome_esperado="$2"
  local pid comando ppid nascimento
  local nossos=() alheios=()

  # Primeiro classifica todos, depois mata. Classificar e matar no mesmo laço fazia a
  # checagem do filho acontecer antes de o pai terminar de cair.
  for pid in $(lsof -ti:"$porta" 2>/dev/null || true); do
    comando="$(ps -o command= -p "$pid" 2>/dev/null || true)"
    [[ -z "$comando" ]] && continue
    ppid="$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ' || true)"
    ppid_comando="$(ps -o command= -p "${ppid:-0}" 2>/dev/null || true)"

    if [[ "$comando" == *"$nome_esperado"* || "$ppid_comando" == *"$nome_esperado"* ]]; then
      nascimento="$(ps -o lstart= -p "$pid" 2>/dev/null | sed -e 's/^ *//' -e 's/ *$//' || true)"
      nossos+=("$pid")
      aviso "Porta $porta ocupada por servidor antigo (PID $pid, de $nascimento)."
    else
      alheios+=("$pid|$comando")
    fi
  done

  for pid in "${nossos[@]:-}"; do
    [[ -n "${pid:-}" ]] && kill "$pid" 2>/dev/null || true
  done

  # Espera a porta sair do ar antes de concluir que sobrou algo alheio: o filho do
  # reloader leva um instante para fechar o socket depois do pai.
  local tentativa=0
  while lsof -ti:"$porta" >/dev/null 2>&1 && (( tentativa < 40 )); do
    sleep 0.25
    tentativa=$(( tentativa + 1 ))
  done

  if lsof -ti:"$porta" >/dev/null 2>&1; then
    for entrada in "${alheios[@]:-}"; do
      [[ -z "${entrada:-}" ]] && continue
      erro "Porta $porta ocupada por algo que não é nosso (PID ${entrada%%|*}):"
      erro "  $(printf '%s' "${entrada#*|}" | cut -c1-100)"
    done
    erro "Libere a porta $porta e rode de novo."
    exit 1
  fi
  [[ ${#nossos[@]} -gt 0 ]] && ok "Porta $porta liberada."
  return 0
}

liberar_porta "$PORTA_BACKEND" uvicorn
[[ $SO_BACKEND -eq 0 ]] && liberar_porta "$PORTA_FRONTEND" next

# ---------------------------------------------------------------------------
# Encerramento limpo
# ---------------------------------------------------------------------------

PIDS=()

# Derruba um serviço e toda a descendência dele, pelo grupo de processos.
derrubar_arvore() {
  local pid="$1"
  [[ -z "${pid:-}" ]] && return 0
  # O sinal para o grupo (`-pid`) é o que alcança os netos; o segundo kill cobre o
  # caso de o processo não ter virado líder de grupo.
  kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
}

ENCERRANDO=0

encerrar() {
  # O trap pode disparar duas vezes (Ctrl+C e depois TERM); a segunda não deve
  # reentrar no meio da limpeza.
  [[ $ENCERRANDO -eq 1 ]] && return
  ENCERRANDO=1

  printf "\n"
  info "Encerrando…"
  for pid in "${PIDS[@]:-}"; do
    derrubar_arvore "$pid"
  done

  # Cinto e suspensório: se alguma coisa sobreviveu, ela aparece ocupando a porta.
  # Deixar um servidor de pé aqui recriaria o problema que motivou o script.
  sleep 1
  insistir_na_porta "$PORTA_BACKEND" uvicorn
  [[ $SO_BACKEND -eq 0 ]] && insistir_na_porta "$PORTA_FRONTEND" next

  ok "Tudo parado."
  exit 0
}

# Mata, com KILL, o que ainda estiver ocupando a porta — só se for nosso.
insistir_na_porta() {
  local porta="$1" nome="$2" pid comando
  for pid in $(lsof -ti:"$porta" 2>/dev/null || true); do
    comando="$(ps -o command= -p "$pid" 2>/dev/null || true)"
    if [[ "$comando" == *"$nome"* ]]; then
      aviso "PID $pid resistiu na porta $porta. Encerrando à força."
      kill -KILL "$pid" 2>/dev/null || true
    fi
  done
}

trap encerrar INT TERM

# ---------------------------------------------------------------------------
# Ollama (camada N4)
# ---------------------------------------------------------------------------

# O container responde à API alguns segundos depois de `up -d`; chamar `ollama
# pull` antes disso falha com erro de conexão.
esperar_ollama() {
  local tentativa=0
  until docker exec vera_ollama ollama list >/dev/null 2>&1; do
    sleep 1
    tentativa=$(( tentativa + 1 ))
    if (( tentativa > 60 )); then
      aviso "O Ollama subiu mas não respondeu em 60s."
      return 1
    fi
  done
}

modelo_presente() {
  docker exec vera_ollama ollama list 2>/dev/null \
    | awk 'NR>1 {print $1}' \
    | grep -qx -e "$MODELO_OLLAMA" -e "${MODELO_OLLAMA}:latest"
}

if [[ $COM_OLLAMA -eq 1 ]]; then
  if ! command -v docker >/dev/null 2>&1; then
    aviso "Docker não encontrado — seguindo sem Ollama. O S-12 vai sair indisponível."
  elif ! docker info >/dev/null 2>&1; then
    aviso "O Docker está instalado mas não está rodando. Abra o Docker Desktop."
    aviso "Seguindo sem Ollama: o S-12 vai sair indisponível."
  else
    # A primeira execução baixa ~1,5 GB de imagem e ~4,7 GB de modelo. Avisar o
    # tamanho antes evita a pessoa achar que travou, e o progresso vai para o
    # terminal e não para o log — esconder uma espera de 15 minutos atrás de uma
    # linha parada é pior do que não ter o aviso.
    if ! docker image inspect "$IMAGEM_OLLAMA" >/dev/null 2>&1; then
      aviso "A imagem do Ollama (~1,5 GB) ainda não está local. Baixando — demora."
    fi
    info "Subindo o Ollama…"
    if ! docker compose up -d ollama; then
      aviso "Falha ao subir o Ollama. Seguindo sem a N4."
      COM_OLLAMA=0
    else
      # Sob `set -e`, um retorno não-zero aqui derrubaria o script inteiro; a espera
      # que falha é tratada logo abaixo, quando o `pull` não encontrar o serviço.
      esperar_ollama || true
      if modelo_presente; then
        ok "Modelo $MODELO_OLLAMA já está no volume."
      else
        aviso "O modelo $MODELO_OLLAMA (~4,7 GB) ainda não foi baixado."
        aviso "Isto leva de 10 a 20 minutos numa conexão boa, e acontece só uma vez:"
        aviso "o modelo fica no volume ollama_data e sobrevive a reinício."
        printf "\n"
        # Sem redirecionar: o `ollama pull` mostra barra de progresso.
        if docker exec vera_ollama ollama pull "$MODELO_OLLAMA"; then
          printf "\n"
        else
          printf "\n"
          aviso "Não consegui baixar o $MODELO_OLLAMA. Seguindo sem a N4."
          COM_OLLAMA=0
        fi
      fi
      if [[ $COM_OLLAMA -eq 1 ]]; then
        ok "Ollama pronto em :11434 (modelo $MODELO_OLLAMA)"
        info "A primeira checagem carrega o modelo na RAM e leva uns 10s a mais."
      fi
    fi
  fi
fi
if [[ $COM_OLLAMA -eq 0 ]]; then
  info "Sem Ollama (use --com-ollama). A N4 vai marcar o S-12 como indisponível,"
  info "que é o comportamento correto por RN-06 — não é erro."
fi

# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------

info "Sincronizando o ambiente Python…"
uv sync --quiet

info "Subindo a API na porta ${PORTA_BACKEND}…"
# `--reload` nunca é opcional aqui: foi a sua falta que deixou um servidor de
# cinco dias servindo código velho sem ninguém perceber.
uv run uvicorn src.main:app \
  --app-dir backend \
  --reload \
  --port "$PORTA_BACKEND" \
  >>"$DIRETORIO_DE_LOGS/backend.log" 2>&1 &
PIDS+=($!)

esperar_saude() {
  local tentativa=0
  until curl -sf "http://127.0.0.1:$PORTA_BACKEND/health" >/dev/null 2>&1; do
    sleep 0.5
    tentativa=$(( tentativa + 1 ))
    if (( tentativa > 60 )); then
      erro "A API não respondeu em 30s. Últimas linhas de logs/backend.log:"
      tail -20 "$DIRETORIO_DE_LOGS/backend.log" >&2
      encerrar
    fi
  done
}
esperar_saude
ok "API no ar: http://localhost:$PORTA_BACKEND  (docs em /docs)"

# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

if [[ $SO_BACKEND -eq 0 ]]; then
  if [[ ! -d "$RAIZ/frontend/node_modules" ]]; then
    info "Instalando dependências do frontend (primeira vez)…"
    (cd "$RAIZ/frontend" && npm install >>"$DIRETORIO_DE_LOGS/frontend.log" 2>&1)
  fi

  # O frontend lê a URL da API daqui; sem o arquivo ele aponta para o padrão e a
  # checagem falha em silêncio no navegador.
  if [[ ! -f "$RAIZ/frontend/.env.local" ]]; then
    cp "$RAIZ/frontend/.env.example" "$RAIZ/frontend/.env.local"
    info "Criei frontend/.env.local a partir do .env.example"
  fi

  info "Subindo o frontend na porta ${PORTA_FRONTEND}…"
  (cd "$RAIZ/frontend" && npm run dev >>"$DIRETORIO_DE_LOGS/frontend.log" 2>&1) &
  PIDS+=($!)

  tentativa=0
  until curl -sf "http://127.0.0.1:$PORTA_FRONTEND" >/dev/null 2>&1; do
    sleep 0.5
    tentativa=$(( tentativa + 1 ))
    if (( tentativa > 120 )); then
      aviso "O frontend demorou mais de 60s. Veja logs/frontend.log"
      break
    fi
  done
  ok "Frontend no ar: http://localhost:$PORTA_FRONTEND"
fi

# ---------------------------------------------------------------------------
# Pronto
# ---------------------------------------------------------------------------

printf "\n${NEGRITO}No ar${N}\n"
printf "  API       http://localhost:%s/docs\n" "$PORTA_BACKEND"
[[ $SO_BACKEND -eq 0 ]] && printf "  Chat      http://localhost:%s\n" "$PORTA_FRONTEND"
printf "  Logs      logs/backend.log"
[[ $SO_BACKEND -eq 0 ]] && printf "  ·  logs/frontend.log"
printf "\n"

printf "\n${NEGRITO}Para testar${N}\n"
cat <<'FIM'
  No chat, nesta ordem:
    1. "oi"                     responde na hora, sem checagem nem porcentagem
    2. uma notícia real          mede estilo, procura corroboração
    3. "URGENTE!!! REPASSEM!!!"  faixa de falsidade, sinais explicando por quê

  Pelo terminal, sem navegador:
    curl -s localhost:8010/api/v1/checar -H 'content-type: application/json' \
      -d '{"texto":"oi, tudo bem?"}' | python3 -m json.tool

  Diagnóstico de uma checagem, sinal por sinal:
    uv run python backend/scripts/debug_pipeline.py "o texto que você quiser"
FIM

printf "\n${CINZA}Ctrl+C derruba tudo.${N}\n\n"

# Segue os logs do backend: é onde aparecem os avisos de GDELT fora do ar e de
# Ollama sem resposta, que antes da auditoria ficavam invisíveis.
tail -f "$DIRETORIO_DE_LOGS/backend.log" &
PIDS+=($!)

wait
