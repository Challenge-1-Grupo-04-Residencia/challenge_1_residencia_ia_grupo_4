from src.core.entities.claim import DocumentoRelacionado
from src.core.ports.news_search import BuscadorDeNoticias
from src.infrastructure.database import SessionLocal, ChecagemCache
from sentence_transformers import SentenceTransformer
from sqlalchemy import text

# Carregamos o modelo apenas 1 vez quando o servidor sobe para não travar a API
print("[BuscadorVetorial] Carregando modelo de IA (isso acontece 1 vez só)...")
try:
    MODELO_EMBEDDING = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"[Aviso] Falha ao carregar o SentenceTransformer: {e}")
    MODELO_EMBEDDING = None

class BuscadorVetorial(BuscadorDeNoticias):
    """
    Busca checagens no nosso próprio banco PostgreSQL usando a extensão pgvector.
    Essa é a memória fotográfica da Vera.
    """
    
    def __init__(self, limiar_minimo: float = 0.70):
        self.limiar_minimo = limiar_minimo

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        if not MODELO_EMBEDDING or not texto.strip():
            return []

        try:
            # 1. Converte o texto do usuário para as coordenadas matemáticas
            vetor_busca = MODELO_EMBEDDING.encode(texto).tolist()
            
            # Formata para o SQL do pgvector: "[0.1, 0.2, ...]"
            vetor_str = str(vetor_busca)

            db = SessionLocal()
            try:
                # 2. Fazemos o banco Postgres calcular a distância (Cosine Distance <=> ou L2 <->)
                # O operador <=> retorna a Cosine Distance (0 = idêntico, 1 = ortogonal, 2 = oposto)
                # Logo, Similaridade = 1 - distancia
                sql = text(f"""
                    SELECT id, texto_alegacao, veredicto, agencia, url_agencia,
                           (1 - (embedding <=> :vetor)) AS similaridade
                    FROM checagens_cache
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> :vetor
                    LIMIT :limite
                """)
                
                resultados = db.execute(sql, {"vetor": vetor_str, "limite": top_k}).fetchall()
                
                documentos = []
                for row in resultados:
                    # Ignoramos coisas que não têm nada a ver (similaridade baixa)
                    if row.similaridade < self.limiar_minimo:
                        continue
                        
                    # 3. Montamos a "prova" para a N4 (Llama) ler
                    # O "titulo" da prova precisa mostrar qual foi o veredicto da agência!
                    texto_prova = f"A {row.agencia} classificou a alegação '{row.texto_alegacao}' como {row.veredicto}."
                    
                    documentos.append(DocumentoRelacionado(
                        titulo=texto_prova,
                        url=row.url_agencia,
                        fonte=row.agencia,
                        similaridade=row.similaridade,
                        fonte_confiavel=True  # 100% de confiança, pois é a nossa base oficial!
                    ))
                
                return documentos
            finally:
                db.close()
                
        except Exception as e:
            print(f"[BuscadorVetorial] Erro na busca: {e}")
            return []
