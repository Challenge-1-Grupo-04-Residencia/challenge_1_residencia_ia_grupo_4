import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.database import SessionLocal, ChecagemCache
from sentence_transformers import SentenceTransformer

def main():
    print("Iniciando o cérebro vetorial da Vera...")
    
    # Carrega o modelo super rápido que gera vetores de tamanho 384
    # É o mesmo tamanho exato que você configurou na coluna `embedding` do banco!
    print("Carregando o modelo de IA 'all-MiniLM-L6-v2'...")
    modelo = SentenceTransformer('all-MiniLM-L6-v2')
    
    db = SessionLocal()
    try:
        # Pega todas as checagens que ainda não têm vetor
        checagens_vazias = db.query(ChecagemCache).filter(ChecagemCache.embedding.is_(None)).all()
        
        total = len(checagens_vazias)
        if total == 0:
            print("Maravilha! Todas as checagens já estão vetorizadas no banco.")
            return

        print(f"Encontrei {total} notícias oficiais sem vetor. Vamos iniciar a conversão matemática!")
        
        lote_tamanho = 500
        for i in range(0, total, lote_tamanho):
            lote_atual = checagens_vazias[i:i+lote_tamanho]
            
            # Puxamos os textos dessas checagens
            textos = [c.texto_alegacao for c in lote_atual]
            
            # A IA transforma os textos em vetores simultaneamente
            embeddings = modelo.encode(textos)
            
            # Atualiza o banco de dados com os novos vetores
            for j, checagem in enumerate(lote_atual):
                checagem.embedding = embeddings[j].tolist()
                
            db.commit()
            print(f"Progresso: {min(i+lote_tamanho, total)} / {total} checagens vetorizadas...")
            
        print("Sucesso! O banco de dados agora tem memória semântica!")
        
    except Exception as e:
        print(f"Deu erro na vetorização: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
