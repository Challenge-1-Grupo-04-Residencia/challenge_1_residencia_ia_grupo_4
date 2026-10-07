"""Orquestração das camadas N0 a N4 (RF-07, RF-08).

As camadas formam um *Chain of Responsibility*: cada uma mede o que sabe medir,
registra seus sinais e repassa adiante — a menos que a regra de parada já tenha sido
atingida, caso em que a corrente termina ali e as camadas mais caras nunca rodam. É
isso que faz a checagem escalar o custo: a LLM da N4 só é chamada quando N0 a N3 não
bastaram (RN-07).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional

from src.core.engine import business_rules, scoring, triagem
from src.core.engine.business_rules import Veredito
from src.core.entities.claim import NoticiaRequest
from src.core.entities.signal import Sinal


@dataclass(frozen=True)
class Evento:
    """Um passo da investigação, para quem está esperando o resultado (RF-03).

    A interface mostrava o andamento por **temporizador**: avançava as etapas em 400 ms,
    1,8 s, 1,2 s, 6 s e 12 s, independentemente do que estivesse acontecendo. Com a N3
    levando de 1 a 25 s e a N4 dependendo de um modelo externo, o que a pessoa via não
    tinha relação com o que a Vera estava fazendo — e, numa ferramenta cujo produto é a
    explicação, inventar o andamento é inventar parte do produto.
    """

    #: ``iniciou`` · ``concluiu`` · ``pulou`` · ``veredito``
    tipo: str
    #: ``TRIAGEM``, ``N2``, ``N3``, ``N4``.
    camada: str
    #: O que a camada tem a dizer, em uma frase, na voz da Vera.
    mensagem: str = ""
    #: Os sinais que esta camada acabou de medir.
    sinais: list[Sinal] = field(default_factory=list)


#: Quem recebe os eventos. ``None`` desliga a notificação, que é o padrão.
Observador = Callable[[Evento], None]

#: O que a Vera está fazendo em cada camada, para a tela dizer em português.
ANUNCIO_DA_CAMADA: dict[str, str] = {
    "TRIAGEM": "Vendo o que é que tu me mandaste…",
    "N0": "Vendo se eu já não conferi isso antes…",
    "N1": "Espiando quem foi que publicou…",
    "N2": "Lendo com atenção o jeito que isso foi escrito…",
    "N3": "Ligando pras minhas comadres pra ver quem mais publicou…",
    "N4": "Conferindo alegação por alegação. Tenha paciência.",
}


class CamadaVerificacao(ABC):
    """Interface base de uma camada de checagem."""

    #: Identificador da camada, usado nos eventos de andamento.
    nome: str = "?"

    def __init__(self):
        self.proxima_camada: Optional["CamadaVerificacao"] = None
        self.C_MIN = scoring.C_MIN
        self.observador: Observador | None = None

    def set_proxima(self, camada: "CamadaVerificacao") -> "CamadaVerificacao":
        """Encadeia a próxima camada e a devolve, para permitir encadeamento fluente."""
        self.proxima_camada = camada
        return camada

    def set_observador(self, observador: Observador | None) -> None:
        """Instala o observador nesta camada e em todas as seguintes."""
        self.observador = observador
        if self.proxima_camada is not None:
            self.proxima_camada.set_observador(observador)

    def _avisar(self, evento: Evento) -> None:
        if self.observador is not None:
            self.observador(evento)

    @abstractmethod
    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        """Mede os sinais desta camada e devolve a notícia, normalmente via ``repassar``."""

    def atingiu_regra_parada(self, noticia: NoticiaRequest) -> bool:
        """Confiança suficiente e score fora da zona de dúvida."""
        return scoring.deve_parar(
            noticia.resultado.veracidade, noticia.resultado.confianca
        )

    def repassar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        """Entrega à próxima camada, ou encerra se a regra de parada foi atingida."""
        desta_camada = [s for s in noticia.resultado.sinais if s.camada == self.nome]
        self._avisar(
            Evento(
                tipo="concluiu",
                camada=self.nome,
                mensagem=self._resumo(desta_camada),
                sinais=desta_camada,
            )
        )

        if not self.proxima_camada:
            return noticia

        if self.atingiu_regra_parada(noticia):
            # RN-07: a pessoa merece saber que a Vera parou porque já tinha resposta, e
            # não porque algo falhou.
            self._avisar(
                Evento(
                    tipo="pulou",
                    camada=self.proxima_camada.nome,
                    mensagem="Já tenho resposta, não precisei ir mais longe.",
                )
            )
            return noticia

        self._avisar(
            Evento(
                tipo="iniciou",
                camada=self.proxima_camada.nome,
                mensagem=ANUNCIO_DA_CAMADA.get(self.proxima_camada.nome, ""),
            )
        )
        return self.proxima_camada.processar(noticia)

    @staticmethod
    def _resumo(sinais: list[Sinal]) -> str:
        """Uma frase sobre o que a camada conseguiu medir.

        Distingue "olhei e não havia o que anotar" de "não consegui apurar": são os dois
        estados nulos do sinal, e dizer "não consegui" sobre um detector que rodou direito
        faria a Vera se acusar de uma falha que não houve.
        """
        if not sinais:
            return "Nada a medir aqui."
        medidos = [s for s in sinais if s.disponivel]
        lacunas = [s for s in sinais if s.e_lacuna]

        if not medidos and not lacunas:
            return "Olhei e não tinha nada para anotar."
        if not medidos:
            return "Não consegui apurar nada aqui."
        frase = f"Medi {len(medidos)} de {len(sinais)}."
        if lacunas:
            frase += f" {len(lacunas)} eu não consegui apurar."
        return frase


class Orquestrador:
    """Constrói a corrente e produz o veredito final."""

    def __init__(self, camada_inicial: CamadaVerificacao):
        self.camada_inicial = camada_inicial

    def checar(
        self,
        noticia: NoticiaRequest,
        observador: Observador | None = None,
    ) -> NoticiaRequest:
        """Roda o pipeline. Devolve a notícia com o resultado acumulado.

        A triagem vem antes da primeira camada: entrada que não é alegação de fato não
        gasta busca externa nem chamada de modelo. Era de onde vinha o "Oi, tudo bem?"
        com 77% de veracidade, e também um custo de GDELT e LLM por saudação recebida.

        ``observador`` recebe um :class:`Evento` por passo, para a interface mostrar o
        andamento de verdade (RF-03).
        """
        self.camada_inicial.set_observador(observador)
        if observador is not None:
            observador(
                Evento(
                    tipo="iniciou",
                    camada="TRIAGEM",
                    mensagem=ANUNCIO_DA_CAMADA["TRIAGEM"],
                )
            )

        natureza = triagem.classificar(noticia.texto)
        if natureza is not triagem.Natureza.ALEGACAO:
            noticia.resultado.natureza = natureza.value
            noticia.resultado.camada_atual = "TRIAGEM"
            noticia.resultado.explicacao = ""
            if observador is not None:
                observador(
                    Evento(
                        tipo="concluiu",
                        camada="TRIAGEM",
                        mensagem="Isso não é notícia pra conferir — é conversa.",
                    )
                )
            return noticia

        if observador is not None:
            observador(
                Evento(
                    tipo="concluiu",
                    camada="TRIAGEM",
                    mensagem="É uma alegação de fato. Vou conferir.",
                )
            )
            observador(
                Evento(
                    tipo="iniciou",
                    camada=self.camada_inicial.nome,
                    mensagem=ANUNCIO_DA_CAMADA.get(self.camada_inicial.nome, ""),
                )
            )
        return self.camada_inicial.processar(noticia)

    def veredito(
        self,
        noticia: NoticiaRequest,
        observador: Observador | None = None,
    ) -> Veredito:
        """Roda o pipeline e aplica as regras de negócio sobre o score final.

        A checagem é considerada encerrada aqui, então RN-04 (confiança baixa vira
        Inconclusivo) passa a valer — durante o pipeline ela não deve valer, senão uma
        camada inicial com pouca cobertura marcaria tudo como inconclusivo.
        """
        processada = self.checar(noticia, observador)
        r = processada.resultado
        contexto = business_rules.Contexto(
            veredito_agencia=r.veredito_agencia,
            agencia=r.agencia,
            dominio_impostor=r.dominio_impostor,
            veiculo_imitado=r.veiculo_imitado,
            natureza=r.natureza,
            pipeline_encerrado=True,
        )
        veracidade = scoring.calcular_veracidade(r.sinais)
        if veracidade is None and r.sinais == []:
            # Nenhuma camada migrou para sinais ainda: respeita o valor gravado direto.
            veracidade = r.veracidade
        return business_rules.aplicar(veracidade, r.confianca, contexto)
