import httpx
import time
import sys
import json

API_URL = "http://localhost:8000/api/v1/checar"

# A Bateria de Testes de Estresse (Red Teaming)
TESTES = [
    {
        "nome": "1. Armadilha da Negação (A prova do Vector Search)",
        "payload": {
            "texto": "Diferente do que andam espalhando, a vacina não tem chip 5G e não altera o DNA. Isso é fake news.", 
            "url": ""
        },
        "veredicto_esperado": ["Verdadeiro", "Inconclusiva"], 
        # Tem que ser Verdadeiro (ele desmente o boato) ou Inconclusivo (se a LLM achar pouco dado), 
        # mas JAMAIS pode ser "Falso", pois o usuário falou algo sensato.
        "descricao": "A IA não pode ler as palavras 'vacina', 'chip' e 'DNA' e classificar como Falso direto. Tem que interpretar a negação."
    },
    {
        "nome": "2. Fake News Gourmet (Enganando a N2)",
        "payload": {
            "texto": "Um estudo recente publicado pela Universidade de Oxford e divulgado pelo Ministério da Saúde (2024) comprovou cientificamente que a aplicação das doses vacinais causa alteração direta na cadeia de DNA de adultos.",
            "url": ""
        },
        "veredicto_esperado": ["Falso", "Inconclusiva"],
        "descricao": "Texto impecável engana a N2, mas a N4 deve contradizer. Essa guerra derruba a confiança, e a Vera ativa sua trava de segurança (RN-04), terminando em Inconclusiva."
    },
    {
        "nome": "3. O Paradoxo do Mentiroso (Enganando a N1)",
        "payload": {
            "texto": "O salário mínimo oficial no Brasil em 2024 foi ajustado para R$ 1.412,00 após aprovação.",
            "url": "https://jornaldacidadeonline.com.br/economia/teste"
        },
        "veredicto_esperado": ["Verdadeiro", "Inconclusiva"],
        "descricao": "O site tem fama péssima (N1 tira ponto), mas a notícia é um fato inegável. A verdade vence a fonte, ou fica Inconclusiva se faltarem dados exatos."
    },
    {
        "nome": "4. Resiliência do Scraper (Paywall / Bloqueio)",
        "payload": {
            "texto": "https://www.nytimes.com/2024/01/01/world/news.html", 
            "url": "https://www.nytimes.com/2024/01/01/world/news.html"
        },
        "veredicto_esperado": ["Inconclusiva"],
        "descricao": "O The New York Times bloqueia robôs. A Vera não pode travar. Ela deve lidar graciosamente e devolver 'Inconclusivo' por falta de acesso ao texto."
    }
]

def rodar_testes():
    print("="*60)
    print("🚀 INICIANDO TESTE ADVERSARIAL DA VERA (E2E) 🚀")
    print("="*60)
    
    try:
        # Testa se a API está online
        httpx.get("http://localhost:8000/docs", timeout=2.0)
    except httpx.ConnectError:
        print("❌ ERRO FATAL: A API não está rodando. Execute 'make api' em outro terminal.")
        sys.exit(1)

    passaram = 0
    falharam = 0

    with httpx.Client(timeout=30.0) as client:
        for i, teste in enumerate(TESTES, 1):
            print(f"\n🧪 TESTE {i}: {teste['nome']}")
            print(f"   Objetivo: {teste['descricao']}")
            
            try:
                inicio = time.time()
                resposta = client.post(API_URL, json=teste["payload"])
                tempo = time.time() - inicio
                
                if resposta.status_code != 200:
                    print(f"   ❌ FALHA CRÍTICA! A API retornou Status HTTP {resposta.status_code}")
                    print(f"      {resposta.text}")
                    falharam += 1
                    continue
                
                dados = resposta.json()
                veredicto = dados.get("faixa", "Erro")
                
                if veredicto in teste["veredicto_esperado"]:
                    print(f"   ✅ PASSOU! Veredito obtido: {veredicto} (Tempo: {tempo:.1f}s)")
                    passaram += 1
                else:
                    print(f"   ❌ FALHOU! Esperava: {teste['veredicto_esperado']} | A Vera respondeu: {veredicto}")
                    print("   [!] Log da Vera:")
                    print(f"       Confiança: {dados.get('confianca')}")
                    print(f"       Explicação: {dados.get('explicacao')}")
                    falharam += 1
                    
            except Exception as e:
                print(f"   ❌ FALHA DE INFRAESTRUTURA: {e}")
                falharam += 1
                
    print("\n" + "="*60)
    print(f"📊 RELATÓRIO FINAL: {passaram} Passaram | {falharam} Falharam")
    print("="*60)

if __name__ == "__main__":
    rodar_testes()
