import time
import os
from src.core.entities.claim import NoticiaRequest
from src.core.engine.n4_nli import CamadaN4Inferencia

# Print de aviso para garantir que o Docker/Ollama esteja ligado
print("🔥 Inicializando laboratório de testes da Camada N4 usando o Ollama local (Docker)...")
print("⚠️ Certifique-se de que o Llama 3 foi baixado (`docker exec -it vera_ollama ollama pull llama3`)\n")

camada_n4 = CamadaN4Inferencia()

def rodar_teste(cenario, noticia_texto, evidencias, resultado_esperado):
    print(f"{"="*10} CENÁRIO: {cenario} {"="*10}")
    print(f"Notícia (A Alegação): '{noticia_texto}'")
    print(f"Evidências encontradas na Internet: {evidencias}")
    print(f"🎯 RESULTADO ESPERADO: {resultado_esperado}\n")

    noticia = NoticiaRequest(texto=noticia_texto)
    # Simulamos o trabalho da N3 inserindo as evidências à mão
    noticia.resultado.evidencias = evidencias
    
    print("🤖 IA Julgando a relação entre os textos...")
    resultado = camada_n4.processar(noticia)
    
    print("\n--- O VEREDITO DA N4 ---")
    print(f"Veracidade Final: {resultado.resultado.veracidade:.2f}")
    print(f"Confiança Final:  {resultado.resultado.confianca:.2f}")
    print(f"Explicação da IA: {resultado.resultado.explicacao}")
    
    # Validação automática
    if resultado_esperado in resultado.resultado.explicacao:
        print("✅ TESTE PASSOU!")
    else:
        print("❌ TESTE FALHOU!")
    print("\n\n")


# === CASO 1: A Mentira Absoluta (Refutação) ===
rodar_teste(
    cenario="FAKE NEWS CLARA",
    noticia_texto="Chá de limão com alho mata completamente o vírus da COVID-19 em 24 horas, afirma estudo vazado.",
    evidencias=[
        "A Organização Mundial da Saúde (OMS) declarou que não existem provas científicas de que chás caseiros ou alho eliminem o vírus da COVID-19.",
        "Infectologistas alertam que o uso de curas milagrosas baseadas em limão não substitui a vacinação e os tratamentos médicos oficiais."
    ],
    resultado_esperado="REFUTA"
)

# === CASO 2: A Verdade Comprovada (Corroboração) ===
rodar_teste(
    cenario="NOTÍCIA VERDADEIRA",
    noticia_texto="O Brasil ganhou a medalha de ouro no futebol masculino nas Olimpíadas do Rio em 2016.",
    evidencias=[
        "Em uma partida emocionante no Maracanã, a seleção brasileira de futebol masculino venceu a Alemanha nos pênaltis e garantiu o ouro inédito nas Olimpíadas de 2016."
    ],
    resultado_esperado="CORROBORA"
)

# === CASO 3: Informação Neutra / Inconclusiva ===
rodar_teste(
    cenario="INCONCLUSIVO (NEUTRO)",
    noticia_texto="O prefeito vai anunciar um novo imposto sobre bicicletas elétricas no mês que vem.",
    evidencias=[
        "O prefeito discursou hoje dizendo que a prefeitura vai investir em novas ciclovias e melhorias para ciclistas.",
        "Câmara de vereadores debate novo projeto de lei sobre impostos veiculares, mas o texto foca apenas em carros a diesel."
    ],
    resultado_esperado="NEUTRO"
)

# === CASO 4: Distorção de Magnitude (Fato Parcial) ===
rodar_teste(
    cenario="DISTORÇÃO PARCIAL",
    noticia_texto="A bolsa de valores caiu impressionantes 50% hoje devido ao novo imposto.",
    evidencias=[
        "O mercado financeiro fechou o dia em leve baixa. O principal índice da bolsa recuou 2% após o anúncio da nova taxação."
    ],
    resultado_esperado="REFUTA"
)

# === CASO 5: Equivalência Semântica Complexa ===
rodar_teste(
    cenario="EQUIVALÊNCIA SEMÂNTICA",
    noticia_texto="A capital da França baniu definitivamente o uso de patinetes elétricos nas ruas.",
    evidencias=[
        "Paris implementou hoje a nova lei municipal proibindo a circulação de e-scooters alugados, após referendo aprovado pela população."
    ],
    resultado_esperado="CORROBORA"
)

# === CASO 6: Distorção Temporal (Fato Antigo como Novo) ===
rodar_teste(
    cenario="DISTORÇÃO TEMPORAL",
    noticia_texto="Urgente: O presidente do Brasil renunciou ao cargo na noite de ontem.",
    evidencias=[
        "O presidente do Brasil assinou ontem um decreto sobre novas regras trabalhistas.",
        "Em 1992, o então presidente do Brasil renunciou ao cargo devido a processos de impeachment."
    ],
    resultado_esperado="REFUTA"
)

# === CASO 7: Correlação vs Causalidade ===
rodar_teste(
    cenario="CORRELAÇÃO VS CAUSALIDADE",
    noticia_texto="Estudo comprova que vacinas da gripe causam autismo em crianças recém-nascidas.",
    evidencias=[
        "Pesquisadores explicam que os sintomas de autismo costumam ser identificados na mesma faixa etária em que as crianças recebem as primeiras vacinas, mas dezenas de estudos globais provam que não existe relação biológica entre os dois eventos."
    ],
    resultado_esperado="REFUTA"
)

# === CASO 8: Citação Fora de Contexto ===
rodar_teste(
    cenario="CITAÇÃO FORA DE CONTEXTO",
    noticia_texto="O Papa declarou hoje publicamente que ama o Diabo e suas obras.",
    evidencias=[
        "Durante a missa de domingo, o Papa discursou: 'Devemos amar o pecador, mas jamais devemos amar o Diabo ou aceitar suas obras tentadoras em nossas vidas'."
    ],
    resultado_esperado="REFUTA"
)

# === CASO 9: Equivalência Numérica / Matemática ===
rodar_teste(
    cenario="EQUIVALÊNCIA NUMÉRICA",
    noticia_texto="A empresa de tecnologia faturou mais de 1 bilhão de reais no último ano.",
    evidencias=[
        "O balanço financeiro divulgado pela corporação registra que o faturamento total do ano passado fechou em 1.250.000.000,00 BRL."
    ],
    resultado_esperado="CORROBORA"
)

# === CASO 10: Irrelevância Total (Neutro) ===
rodar_teste(
    cenario="IRRELEVÂNCIA (NEUTRO)",
    noticia_texto="Elon Musk comprou a rede de fast food McDonald's.",
    evidencias=[
        "Elon Musk, dono da Tesla, concluiu a polêmica aquisição do Twitter por 44 bilhões de dólares.",
        "O McDonald's anunciou hoje o lançamento de um novo hambúrguer vegano."
    ],
    resultado_esperado="NEUTRO"
)

