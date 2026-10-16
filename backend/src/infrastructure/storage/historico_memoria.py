"""Histórico de checagens em memória (RF-42, RF-43).

Implementação de partida: destrava o feed da página inicial sem exigir decisão de banco
de dados, que ainda não foi tomada pelo grupo.

**O conteúdo se perde ao reiniciar o servidor.** Para produção isso precisa virar
persistência de verdade — a porta ``HistoricoDeChecagens`` existe justamente para que a
troca não toque no núcleo nem na API.
"""

import threading
from collections import OrderedDict

from src.core.entities.checagem_registrada import ChecagemRegistrada

#: Quantas checagens ficam guardadas. O feed mostra no máximo algumas dezenas, e sem
#: teto um servidor de longa duração cresceria sem limite.
CAPACIDADE_PADRAO = 200


class HistoricoEmMemoria:
    """Guarda as últimas checagens, descartando as mais antigas."""

    def __init__(self, capacidade: int = CAPACIDADE_PADRAO):
        self.capacidade = capacidade
        self._itens: OrderedDict[str, ChecagemRegistrada] = OrderedDict()
        # O uvicorn atende requisições concorrentes, e as rotas síncronas rodam em
        # threads diferentes: sem o lock, duas checagens simultâneas podem corromper a
        # ordem do OrderedDict.
        self._trava = threading.Lock()

    def registrar(self, checagem: ChecagemRegistrada) -> None:
        with self._trava:
            self._itens[checagem.id] = checagem
            self._itens.move_to_end(checagem.id)
            while len(self._itens) > self.capacidade:
                self._itens.popitem(last=False)

    def recentes(self, limite: int = 10) -> list[ChecagemRegistrada]:
        with self._trava:
            todas = list(self._itens.values())
        return list(reversed(todas))[: max(0, limite)]

    def buscar(self, id_checagem: str) -> ChecagemRegistrada | None:
        with self._trava:
            return self._itens.get(id_checagem)
