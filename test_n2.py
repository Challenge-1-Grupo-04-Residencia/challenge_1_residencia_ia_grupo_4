from src.core.entities.claim import NoticiaRequest
from src.core.engine.n2_content import CamadaN2Conteudo

# 1. Instanciamos a nossa camada N2
camada_n2 = CamadaN2Conteudo()

# 2. Criamos uma notícia de teste (texto que parece fake news por causa de gritos e urgência)
noticia_teste = NoticiaRequest(
    texto="URGENTE!!! REPASSEM PARA TODOS OS SEUS CONTATOS!!! Vacina causa autismo e o governo está escondendo as provas definitivas disso! Acordem!!!"
)

print(f"--- ANTES DA CAMADA N2 ---")
print(f"Veracidade: {noticia_teste.resultado.veracidade}")
print(f"Confiança: {noticia_teste.resultado.confianca}")

# 3. Processamos a notícia
resultado_n2 = camada_n2.processar(noticia_teste)

print(f"\n--- DEPOIS DA CAMADA N2 ---")
print(f"Camada atual: {resultado_n2.resultado.camada_atual}")
print(f"Veracidade: {resultado_n2.resultado.veracidade:.2f}")
print(f"Confiança: {resultado_n2.resultado.confianca:.2f}")
print(f"Explicação: {resultado_n2.resultado.explicacao}")
