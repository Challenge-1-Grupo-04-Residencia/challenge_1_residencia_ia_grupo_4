import asyncio
from src.core.engine.n2_content import CamadaN2Conteudo
from src.core.engine.n3_corroboration import CamadaN3Corroboracao
from src.core.engine.n4_nli import CamadaN4Inferencia
from src.core.engine.orchestrator import Orquestrador
from src.core.entities.claim import NoticiaRequest
from src.infrastructure.search.gdelt import BuscadorGdelt

def run():
    print("Montando o pipeline N2 -> N3 -> N4...")
    n2 = CamadaN2Conteudo()
    n3 = CamadaN3Corroboracao(BuscadorGdelt())
    n4 = CamadaN4Inferencia()
    n2.set_proxima(n3).set_proxima(n4)
    orquestrador = Orquestrador(n2)

    noticia_falsa = NoticiaRequest(
        texto="Chá de limão com alho mata completamente o vírus da COVID-19 em 24 horas."
    )
    
    print("\nEnviando Notícia para a Senhora Vera (Aguarde a busca GDELT e o LLM)...")
    print(f"Alegação: '{noticia_falsa.texto}'\n")
    
    veredito = orquestrador.veredito(noticia_falsa)
    resultado = noticia_falsa.resultado

    print("========================================")
    print(f"Veredito Final: {veredito.faixa.value}")
    print(f"Veracidade: {veredito.veracidade}%")
    print(f"Confiança: {veredito.confianca:.2f}")
    print(f"Camada de Parada: {resultado.camada_atual}")
    print("\nExplicação da Vera:")
    print(veredito.motivo_regra or "")
    print(resultado.explicacao)
    print("\nSinais Ativados:")
    for s in resultado.sinais:
        print(f"- {s.id} ({s.peso} pts): {s.score}")

if __name__ == "__main__":
    run()
