import sys
import os

# Esse truque garante que o script enxergue a pasta 'src' do backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.database import SessionLocal, iniciar_banco, ChecagemCache

def popular_banco():
    print("1. Criando tabelas no Postgres (Migration Inicial)...")
    iniciar_banco()

    print("2. Semeando dados de teste (Seed)...")
    with SessionLocal() as db:
        url_teste = "https://g1.globo.com/politica/noticia/2026/09/30/mendonca-vota-para-confirmar-decisao-que-tirou-do-ar-posts-sobre-nossa-senhora-aparecida.ghtml"
        
        existe = db.query(ChecagemCache).filter(ChecagemCache.url_agencia == url_teste).first()
        
        if not existe:
            noticia = ChecagemCache(
                texto_alegacao="Decisão sobre os posts da Nossa Senhora Aparecida.",
                veredicto="Verdadeiro",
                agencia="Agência Lupa",
                url_agencia=url_teste
            )
            db.add(noticia)
            db.commit()
            print("✅ Link do G1 salvo no Cache da Vera com sucesso!")
        else:
            print("⚠️ A notícia já estava lá!")

if __name__ == "__main__":
    popular_banco()
