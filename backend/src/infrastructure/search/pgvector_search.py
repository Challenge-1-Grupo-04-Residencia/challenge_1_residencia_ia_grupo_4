from src.core.engine.checagens_publicadas import _tem_negacao, veredito_no_titulo
from src.core.entities.claim import DocumentoRelacionado
from src.core.ports.news_search import BuscadorDeNoticias
from src.infrastructure.database import SessionLocal, ChecagemCache
from src.infrastructure.search.embeddings import gerar_embedding
from sqlalchemy import text

# O modelo de embedding NÃO é mais carregado no import deste módulo: carregar o
# SentenceTransformer aqui travava a primeira checagem em produção (e estourava os
# 512 MB do Render). O carregamento agora é preguiçoso e thread-safe — ver
# ``src.infrastructure.search.embeddings``.


def _formatar_titulo_checagem(texto_alegacao: str, veredicto: str) -> str:
    """Formata o título da checagem sem criar dupla negação para a N3/N4."""
    alegacao = (texto_alegacao or "").strip()
    v_norm = (veredicto or "").strip().lower()
    v_titulo = veredito_no_titulo(alegacao)

    if v_norm == "falso":
        if v_titulo == "falso" or _tem_negacao(alegacao):
            return alegacao
        return f"É falso que {alegacao}"
    if v_norm == "verdadeiro":
        if v_titulo == "verdadeiro":
            return alegacao
        return f"É verdade que {alegacao}"
    return alegacao


class BuscadorVetorial(BuscadorDeNoticias):
    """
    Busca checagens no nosso próprio banco PostgreSQL usando a extensão pgvector.
    Essa é a memória fotográfica da Vera.
    """
    
    def __init__(self, limiar_minimo: float = 0.70):
        self.limiar_minimo = limiar_minimo

    def buscar(self, texto: str, top_k: int = 5) -> list[DocumentoRelacionado]:
        if not texto.strip():
            return []

        try:
            # 1. Converte o texto do usuário para as coordenadas matemáticas
            vetor_busca = gerar_embedding(texto)
            if vetor_busca is None:
                return []
            
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
                        
                    # 3. Montamos a "prova" sem dupla negação para a N3 e a N4 (Llama) lerem
                    texto_prova = _formatar_titulo_checagem(row.texto_alegacao, row.veredicto)
                    eh_verdadeiro = str(row.veredicto or "").strip().lower() == "verdadeiro"
                    
                    documentos.append(DocumentoRelacionado(
                        titulo=texto_prova,
                        url=row.url_agencia,
                        fonte=row.agencia,
                        similaridade=row.similaridade,
                        # Só checagens com veredicto verdadeiro podem corroborar um fato no S-11
                        fonte_confiavel=eh_verdadeiro,
                    ))
                
                return documentos
            finally:
                db.close()
                
        except Exception as e:
            print(f"[BuscadorVetorial] Erro na busca: {e}")
            return []
