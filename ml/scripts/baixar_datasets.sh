#!/usr/bin/env bash
# Baixa, padroniza e documenta os datasets em PT-BR da fase Investigate.
#
#   ./scripts/baixar_datasets.sh              # baixa o que falta e gera a documentação
#   ./scripts/baixar_datasets.sh --docs       # só refaz padronização e documentação
#   ./scripts/baixar_datasets.sh --so fake-br # apenas um dataset
#   ./scripts/baixar_datasets.sh --completo   # inclui downloads pesados (FKTC, 460 MB)
#
# Tudo vai para datasets/, que está fora do controle de versão.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec uv run --with pandas --with pyarrow python scripts/datasets.py "$@"
