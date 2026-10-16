"""Marca-passo e disjuntor, compartilhados pelos adaptadores de busca.

Os dois nasceram dentro do adaptador do GDELT e saíram para cá quando o segundo
provedor entrou: são política de uso de serviço externo, não detalhe de um provedor.

A medição de 05/10 mostrou por que ambos são necessários. Sem marca-passo, duas
requisições simultâneas chegam juntas na API e tomam ``HTTP 429`` juntas — o endpoint
roda em *threadpool*, então isso acontece com dois usuários. Sem disjuntor, com o
serviço fora do ar **toda** checagem paga o timeout inteiro para chegar à mesma
conclusão da anterior: eram 25 s de espera por usuário, sempre.
"""

import logging
import threading
import time

_log = logging.getLogger(__name__)


class Marcapasso:
    """Garante um intervalo mínimo entre chamadas à mesma API, entre threads.

    O limite dos provedores é por IP, não por objeto, então a instância que importa é
    uma por provedor e compartilhada — ver os módulos dos adaptadores.
    """

    def __init__(self, intervalo: float):
        self._intervalo = intervalo
        self._trava = threading.Lock()
        self._ultima_chamada = 0.0

    def aguardar(self) -> None:
        with self._trava:
            espera = self._intervalo - (time.monotonic() - self._ultima_chamada)
            if espera > 0:
                time.sleep(espera)
            self._ultima_chamada = time.monotonic()


class Disjuntor:
    """Para de tentar depois de algumas falhas seguidas, e volta a tentar depois.

    Também é questão de boa vizinhança: insistir numa API que acabou de nos pedir para
    desacelerar é o que mantém o 429 vindo.

    Um sucesso fecha o disjuntor. Enquanto ele está aberto, a camada recebe o erro na
    hora e por RN-06 o sinal fica indisponível — o mesmo resultado de antes, sem a
    espera.
    """

    def __init__(self, nome: str, falhas_para_abrir: int, descanso: float):
        self._nome = nome
        self._falhas_para_abrir = falhas_para_abrir
        self._descanso = descanso
        self._trava = threading.Lock()
        self._falhas = 0
        self._aberto_desde = 0.0

    def aberto(self) -> bool:
        with self._trava:
            if self._falhas < self._falhas_para_abrir:
                return False
            if time.monotonic() - self._aberto_desde >= self._descanso:
                # Passado o descanso, deixa uma tentativa passar para sondar o serviço,
                # que pode ter voltado. O disjuntor não pode fechar a camada para sempre.
                self._falhas = self._falhas_para_abrir - 1
                return False
            return True

    def registrar_falha(self) -> None:
        with self._trava:
            self._falhas += 1
            if self._falhas == self._falhas_para_abrir:
                self._aberto_desde = time.monotonic()
                _log.warning(
                    "%s: %d falhas seguidas, parando de tentar por %.0fs",
                    self._nome,
                    self._falhas,
                    self._descanso,
                )

    def registrar_sucesso(self) -> None:
        with self._trava:
            self._falhas = 0
