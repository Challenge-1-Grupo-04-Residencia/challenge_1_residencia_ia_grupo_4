"""Gerador de embeddings da busca vetorial (N3), carregado sob demanda.

## Por que este módulo existe

O ``pgvector_search`` instanciava ``SentenceTransformer('all-MiniLM-L6-v2')`` **no
import**. Em produção (Render Free: 512 MB de RAM, 0,1 vCPU) isso significava:

* importar o PyTorch — a roda do PyPI traz ~2,7 GB de bibliotecas CUDA para uma máquina
  sem GPU — e baixar os pesos do Hugging Face a cada *cold start*;
* fazer tudo isso **dentro da primeira requisição de checagem**, antes de qualquer byte
  do SSE sair: a tela congelava em "Vendo o pedido..." até o proxy cortar a conexão,
  quando o processo não era morto antes por falta de memória.

Agora o padrão é o ``fastembed`` (ONNX Runtime): o mesmo ``all-MiniLM-L6-v2``, os
mesmos 384 números por texto (compatíveis com os vetores já gravados no Supabase), com
uma fração da RAM e sem PyTorch. O modelo é baixado no *build* da imagem e carregado uma
vez só, sob trava, na primeira vez que alguém precisa dele (ou no aquecimento do
servidor — ver ``main.py``).

## Configuração (variável ``VERA_EMBEDDINGS``)

* ``auto`` (padrão): tenta ``fastembed``; se não estiver instalado, tenta
  ``sentence-transformers`` (útil em máquina de desenvolvimento que já o tem).
* ``fastembed`` / ``sentence-transformers``: força um dos motores.
* ``off``: desliga a busca vetorial. A N3 segue só com o Google Notícias — é a saída de
  emergência para uma máquina sem memória nenhuma sobrando.

Falha ao carregar **nunca** derruba a checagem: o buscador vetorial devolve lista
vazia e o híbrido segue com as outras fontes (RN-06).
"""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Protocol

_log = logging.getLogger(__name__)

#: Nome do modelo, o mesmo usado em ``scripts/vetorizar_banco.py`` para semear o banco.
MODELO = "sentence-transformers/all-MiniLM-L6-v2"
DIMENSOES = 384


class _Motor(Protocol):
    def __call__(self, texto: str) -> list[float]: ...


_trava = threading.Lock()
_motor: _Motor | None = None
_tentou = False
_descricao = "não carregado"


def _carregar_fastembed() -> _Motor:
    from fastembed import TextEmbedding

    # Uma thread só: com 0,1 vCPU, mais threads só disputam a mesma fatia de CPU.
    modelo = TextEmbedding(
        MODELO,
        threads=int(os.environ.get("VERA_EMBEDDINGS_THREADS", "1")),
        cache_dir=os.environ.get("FASTEMBED_CACHE_PATH"),
    )

    def gerar(texto: str) -> list[float]:
        return [float(x) for x in next(iter(modelo.embed([texto])))]

    return gerar


def _carregar_sentence_transformers() -> _Motor:
    from sentence_transformers import SentenceTransformer

    modelo = SentenceTransformer(MODELO, device="cpu")

    def gerar(texto: str) -> list[float]:
        return modelo.encode(texto).tolist()

    return gerar


_MOTORES = {
    "fastembed": _carregar_fastembed,
    "sentence-transformers": _carregar_sentence_transformers,
}


def _carregar() -> None:
    global _motor, _tentou, _descricao
    escolha = os.environ.get("VERA_EMBEDDINGS", "auto").strip().lower()
    if escolha == "off":
        _descricao = "desligado (VERA_EMBEDDINGS=off)"
        _log.warning("Busca vetorial desligada por VERA_EMBEDDINGS=off.")
        return

    candidatos = list(_MOTORES) if escolha == "auto" else [escolha]
    for nome in candidatos:
        fabrica = _MOTORES.get(nome)
        if fabrica is None:
            _log.error("VERA_EMBEDDINGS=%s não é um motor conhecido.", nome)
            continue
        inicio = time.perf_counter()
        try:
            _motor = fabrica()
        except ImportError:
            _log.info("Motor de embeddings %s não está instalado.", nome)
            continue
        except Exception:  # noqa: BLE001 - modelo indisponível não derruba a API
            _log.exception("Falha ao carregar o motor de embeddings %s.", nome)
            continue
        _descricao = f"{nome} ({time.perf_counter() - inicio:.1f}s para carregar)"
        _log.info("Embeddings prontos: %s", _descricao)
        return
    _descricao = "indisponível"
    _log.warning("Nenhum motor de embeddings disponível; busca vetorial desligada.")


def obter_motor() -> _Motor | None:
    """Devolve a função de embedding, carregando-a na primeira chamada (thread-safe)."""
    global _tentou
    if _tentou:
        return _motor
    with _trava:
        if not _tentou:
            try:
                _carregar()
            finally:
                _tentou = True
    return _motor


def gerar_embedding(texto: str) -> list[float] | None:
    """Vetor de 384 posições do texto, ou ``None`` se não houver motor disponível."""
    motor = obter_motor()
    if motor is None or not texto.strip():
        return None
    return motor(texto)


def estado() -> str:
    """Descrição curta para o endpoint de prontidão."""
    return _descricao
