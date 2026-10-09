import os
from sqlalchemy import create_engine,Column, Integer, String, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://vera_user:vera_pass@localhost:5432/vera_db"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ChecagemCache(Base):
    __tablename__= "checagens_cache"

    id = Column(Integer,primary_key=True, index=True)
    texto_alegacao = Column(Text, nullable=False)

    # Aqui vamos usar a coluna vetorial, 384 é o tamanho do vetor do modelo de embedins
    embedding = Column(Vector(384))

    veredicto = Column(String(50), nullable=False)

    agencia = Column(String(100))

    url_agencia = Column(String(255))

class DominioReputacao(Base):
    """Ficha criminal de cada site/domínio. Quantas verdades vs fake news ele já postou."""
    __tablename__ = "dominios_reputacao"

    dominio = Column(String(255), primary_key=True, index=True)
    total_noticias = Column(Integer, default=0)
    noticias_falsas = Column(Integer, default=0)
    noticias_verdadeiras = Column(Integer, default=0)
    
    # Score de 0 a 100. (ex: 100 = Só posta verdade, 0 = Só posta mentira)
    score_confiabilidade = Column(Integer, default=50)

class HistoricoAvaliacaoLote(Base):
    """Guarda os resultados das avaliações em lote feitas nos datasets."""
    __tablename__ = "historico_avaliacoes"

    id = Column(Integer, primary_key=True, index=True)
    data_execucao = Column(String(50), nullable=False) # Armazena ISO string
    dataset = Column(String(100), nullable=False)
    qtd_amostras = Column(Integer, nullable=False)
    acuracia = Column(Integer, nullable=False) # %
    taxa_falsos_positivos = Column(Integer, nullable=False) # %
    taxa_inconclusivos = Column(Integer, nullable=False) # %
    tempo_medio_ms = Column(Integer, nullable=False)

def iniciar_banco():
    """Ativa a extensão de IA no Postgres e cria as tabelas"""
    with engine.connect() as conn:
        #ativa o vetorial dentro do postgres
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=engine)