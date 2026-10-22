# Imagem de produção da API (Render Free: 512 MB RAM, 0,1 vCPU).
#
# Dois estágios: o primeiro instala as dependências e baixa o modelo de embeddings; o
# segundo leva só o resultado, sem o uv e sem cache de build.

# ---------------------------------------------------------------- build
FROM python:3.12-slim-bookworm AS build

# Copia o binário do UV super rápido direto da imagem oficial dos criadores
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/

WORKDIR /app

# Variáveis de ambiente para otimizar o UV dentro do Docker
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    # TRUQUE DE INFRA: Limita os downloads paralelos para não travar a rede do Docker no Mac
    UV_CONCURRENT_DOWNLOADS=4 \
    UV_CONCURRENT_INSTALLS=4

# Copia apenas os arquivos de dependência primeiro (para aproveitar o cache do Docker)
COPY pyproject.toml uv.lock ./

# Só as dependências de produção (`--no-dev` deixa de fora notebooks, mkdocs, pandas e
# o PyTorch/CUDA do sentence-transformers, que viviam aqui e somavam ~7 GB).
RUN uv sync --frozen --no-install-project --no-dev

# Baixa o modelo de embeddings NO BUILD. Antes ele era baixado do Hugging Face em tempo
# de execução, dentro da primeira checagem, a cada cold start do plano gratuito.
ENV FASTEMBED_CACHE_PATH=/app/.cache/fastembed
RUN /app/.venv/bin/python -c "from fastembed import TextEmbedding; \
TextEmbedding('sentence-transformers/all-MiniLM-L6-v2', cache_dir='${FASTEMBED_CACHE_PATH}')"

# Agora copia o código fonte (backend/ contém src/ e tests/)
COPY backend /app/backend

# Sincroniza o projeto final
RUN uv sync --frozen --no-dev

# ---------------------------------------------------------------- runtime
FROM python:3.12-slim-bookworm

WORKDIR /app
RUN useradd --create-home --uid 1000 vera
COPY --from=build --chown=vera:vera /app /app
USER vera

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FASTEMBED_CACHE_PATH=/app/.cache/fastembed \
    # Com 0,1 vCPU, mais threads só disputam a mesma fatia de CPU e gastam RAM.
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false \
    # Menos arenas do glibc: corta bastante a RAM residual de processos com threads.
    MALLOC_ARENA_MAX=2 \
    HF_HUB_OFFLINE=1 \
    PORT=8000

# Expõe a porta que o FastAPI vai rodar
EXPOSE 8000

# Chama o uvicorn do venv direto: `uv run` em produção podia tentar sincronizar o
# ambiente (inclusive o grupo dev) no boot. Um worker só, porque cada worker carrega o
# próprio modelo e dois não cabem em 512 MB. `--app-dir backend` mantém os imports
# `from src....`. O keep-alive acima de 60 s evita que a Render/Cloudflare reutilize
# uma conexão que o uvicorn acabou de fechar (502 intermitente).
CMD ["sh", "-c", "exec uvicorn src.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --proxy-headers --forwarded-allow-ips='*' --timeout-keep-alive 75"]
