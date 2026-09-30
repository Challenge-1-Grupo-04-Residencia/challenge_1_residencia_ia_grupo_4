# Usa uma imagem oficial do Python, leve (slim)
FROM python:3.12-slim-bookworm

# Copia o binário do UV super rápido direto da imagem oficial dos criadores
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Variáveis de ambiente para otimizar o UV dentro do Docker
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# TRUQUE DE INFRA: Limita os downloads paralelos para não travar a rede do Docker no Mac
ENV UV_CONCURRENT_DOWNLOADS=4
ENV UV_CONCURRENT_INSTALLS=4

# Copia apenas os arquivos de dependência primeiro (para aproveitar o cache do Docker)
COPY pyproject.toml uv.lock ./

# Instala as dependências travadas pelo lockfile (sem as de desenvolvimento)
RUN uv sync --frozen --no-install-project --no-dev

# Agora copia o código fonte e os testes (backend/ contém src/ e tests/)
COPY backend /app/backend

# Sincroniza o projeto final
RUN uv sync --frozen --no-dev

# Expõe a porta que o FastAPI vai rodar
EXPOSE 8000

# Comando para rodar o servidor, usando o próprio UV para invocar o uvicorn
# --app-dir backend coloca backend/ no sys.path, mantendo os imports `from src....`
CMD ["uv", "run", "uvicorn", "src.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]
