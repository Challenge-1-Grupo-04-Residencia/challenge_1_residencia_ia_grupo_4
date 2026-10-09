.PHONY: help up down build logs db ollama-model install api front setup-db ingest-db ingest-n1 ingest-vetores seed test test-front check avaliar clean

help: ## Mostra os comandos disponíveis
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ==========================================
# AMBIENTE DOCKER
# ==========================================
up: ## Sobe todo o ambiente via Docker em segundo plano
	docker compose up -d

down: ## Derruba todos os containers do projeto
	docker compose down

build: ## Reconstrói as imagens do Docker
	docker compose build

logs: ## Exibe os logs de todos os containers em tempo real
	docker compose logs -f

db: ## Sobe apenas o Postgres com PGVector
	docker compose up -d postgres

ollama-model: ## Baixa o modelo llama3 no Ollama para a Camada N4
	docker compose exec vera_ollama ollama pull llama3

# ==========================================
# DESENVOLVIMENTO LOCAL
# ==========================================
install: ## Sincroniza dependências do backend e instala pacotes do frontend
	uv sync
	npm --prefix frontend install

api: ## Roda a API com hot-reload na porta padrão do time (8010)
	uv run uvicorn src.main:app --app-dir backend --reload --port 8010

front: ## Roda o frontend Next.js em desenvolvimento
	npm --prefix frontend run dev

# ==========================================
# BANCO DE DADOS & INGESTÃO
# ==========================================
seed: setup-db ingest-db ingest-n1 ingest-vetores ## Roda todo o pipeline de banco e dados em sequência (N0, N1, N3)

setup-db: ## Prepara tabelas e dados iniciais no banco
	uv run python backend/scripts/setup_db.py

ingest-db: ## Ingestão massiva de datasets para a Camada N0
	uv run python backend/scripts/ingestao.py

ingest-n1: ## Calcula reputação de sites para a Camada N1
	uv run python backend/scripts/ingestao_reputacao.py

ingest-vetores: ## Vetoriza checagens para busca semântica na N3
	uv run python backend/scripts/vetorizar_banco.py

# ==========================================
# TESTES E QUALIDADE
# ==========================================
test: ## Roda testes unitários do backend (Pytest)
	uv run pytest

test-front: ## Roda testes do frontend (Vitest)
	npm --prefix frontend test

check: test test-front ## Roda a suíte completa de testes (backend + frontend) e typecheck
	npm --prefix frontend run build

avaliar: ## Roda a auditoria de benchmark em todos os datasets principais da documentação
	uv run python scripts/avaliar_modelo.py --dataset todos --n 20

clean: ## Limpa caches temporários de Python e Next.js
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache frontend/.next
