"""Porta do histórico de checagens (RF-42, RF-43).

Guarda o que a Vera já checou, para alimentar o feed da página inicial e, mais adiante,
o histórico por usuário. O núcleo depende desta interface e não de banco nenhum.

Separado do cache da N0 de propósito: o cache existe para **evitar recomputar** uma
checagem dentro do prazo de validade (RN-09), enquanto o histórico existe para
**mostrar** o que já foi checado. Os dois podem vir a compartilhar armazenamento, mas
respondem a perguntas diferentes e têm regras de expiração diferentes.
"""

from typing import Protocol

from src.core.entities.checagem_registrada import ChecagemRegistrada


class HistoricoDeChecagens(Protocol):
    """Registro do que a Vera já checou."""

    def registrar(self, checagem: ChecagemRegistrada) -> None:
        """Guarda uma checagem concluída.

        Implementações não devem levantar exceção por falha de escrita: perder uma
        entrada do feed não pode derrubar a resposta ao usuário, que é o que importa.
        """
        ...

    def recentes(self, limite: int = 10) -> list[ChecagemRegistrada]:
        """As checagens mais recentes, da mais nova para a mais antiga."""
        ...

    def buscar(self, id_checagem: str) -> ChecagemRegistrada | None:
        """Recupera uma checagem pelo identificador, ou ``None`` se não existir."""
        ...
