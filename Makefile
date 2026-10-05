.PHONY: help up down build logs api front db setup-db test

help: ## Mostra os comandos disponíveis
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ==========================================
# COMANDOS DOCKER (Ambiente Completo)
# ==========================================
up: ## Sobe todo o ambiente via Docker (API, Banco, Ollama) em segundo plano
	docker-compose up -d

down: ## Derruba todos os containers do projeto
	docker-compose down

build: ## Reconstrói as imagens do Docker (útil quando adicionar bibliotecas novas)
	docker-compose build

logs: ## Exibe os logs de todos os containers em tempo real
	docker-compose logs -f

# ==========================================
# COMANDOS LOCAIS DE DESENVOLVIMENTO
# ==========================================
db: ## Sobe apenas o Banco de Dados (Postgres) via Docker
	docker-compose up -d postgres

api: ## Roda a API do Backend localmente usando o UV (Hot-Reload ativado)
	uv run uvicorn src.main:app --app-dir backend --reload --port 8000

front: ## Roda o Frontend localmente no modo de desenvolvimento
	cd frontend && npm run dev

setup-db: ## Prepara as tabelas do banco e injeta a notícia de teste (Migration/Seed)
	uv run python backend/scripts/setup_db.py

ingest-db: ## Roda a ingestão massiva dos Datasets reais para a Camada N0
	uv run python backend/scripts/ingestao.py

ingest-n1: ## Calcula a nota de reputação dos sites e injeta na tabela da Camada N1
	uv run python backend/scripts/ingestao_reputacao.py

ingest-vetores: ## Converte as checagens da N0 em vetores matemáticos para a Busca Semântica da N3
	uv run python backend/scripts/vetorizar_banco.py

test: ## Roda todos os testes unitários do Backend usando Pytest
	uv run pytest
