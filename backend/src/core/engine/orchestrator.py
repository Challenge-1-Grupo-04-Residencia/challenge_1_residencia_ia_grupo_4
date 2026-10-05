"""Orquestração das camadas N0 a N4 (RF-07, RF-08).

As camadas formam um *Chain of Responsibility*: cada uma mede o que sabe medir,
registra seus sinais e repassa adiante — a menos que a regra de parada já tenha sido
atingida, caso em que a corrente termina ali e as camadas mais caras nunca rodam. É
isso que faz a checagem escalar o custo: a LLM da N4 só é chamada quando N0 a N3 não
bastaram (RN-07).
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.core.engine import business_rules, scoring, triagem
from src.core.engine.business_rules import Veredito
from src.core.entities.claim import NoticiaRequest


class CamadaVerificacao(ABC):
    """Interface base de uma camada de checagem."""

    def __init__(self):
        self.proxima_camada: Optional["CamadaVerificacao"] = None
        self.C_MIN = scoring.C_MIN

    def set_proxima(self, camada: "CamadaVerificacao") -> "CamadaVerificacao":
        """Encadeia a próxima camada e a devolve, para permitir encadeamento fluente."""
        self.proxima_camada = camada
        return camada

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
        if self.proxima_camada and not self.atingiu_regra_parada(noticia):
            return self.proxima_camada.processar(noticia)
        return noticia


class Orquestrador:
    """Constrói a corrente e produz o veredito final."""

    def __init__(self, camada_inicial: CamadaVerificacao):
        self.camada_inicial = camada_inicial

    def checar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        """Roda o pipeline. Devolve a notícia com o resultado acumulado.

        A triagem vem antes da primeira camada: entrada que não é alegação de fato não
        gasta busca externa nem chamada de modelo. Era de onde vinha o "Oi, tudo bem?"
        com 77% de veracidade, e também um custo de GDELT e LLM por saudação recebida.
        """
        natureza = triagem.classificar(noticia.texto)
        if natureza is not triagem.Natureza.ALEGACAO:
            noticia.resultado.natureza = natureza.value
            noticia.resultado.camada_atual = "TRIAGEM"
            noticia.resultado.explicacao = ""
            return noticia
        return self.camada_inicial.processar(noticia)

    def veredito(self, noticia: NoticiaRequest) -> Veredito:
        """Roda o pipeline e aplica as regras de negócio sobre o score final.

        A checagem é considerada encerrada aqui, então RN-04 (confiança baixa vira
        Inconclusivo) passa a valer — durante o pipeline ela não deve valer, senão uma
        camada inicial com pouca cobertura marcaria tudo como inconclusivo.
        """
        processada = self.checar(noticia)
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
