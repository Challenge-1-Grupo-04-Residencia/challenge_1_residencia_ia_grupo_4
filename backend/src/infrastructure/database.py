import logging
import os
import re
from sqlalchemy import create_engine,Column, Integer, String, Text, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector

_log = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://vera_user:vera_pass@localhost:5432/vera_db"
)
# Painéis (Supabase, Render, Heroku) entregam `postgres://`, que o SQLAlchemy 2 recusa.
DATABASE_URL = re.sub(r"^postgres(ql)?://", "postgresql+psycopg2://", DATABASE_URL)

# O host direto do Supabase (`db.<ref>.supabase.co`) só tem endereço IPv6, e a Render
# não tem saída IPv6: a conexão falha ou fica pendurada até o timeout do TCP. Em nuvem
# sem IPv6, use a URL do *pooler* (Supavisor), que tem IPv4. Ver docs/deploy-nuvem.md.
if re.search(r"@db\.[a-z0-9]+\.supabase\.co", DATABASE_URL):
    _log.warning(
        "DATABASE_URL aponta para o host direto do Supabase (somente IPv6). Se o "
        "provedor não tiver IPv6 (Render, Vercel, Heroku...), use a URL do pooler: "
        "postgres.<ref>@aws-X-<regiao>.pooler.supabase.com:5432."
    )

# Sem estes limites, um banco inalcançável segurava a thread da checagem pelo timeout
# do sistema operacional (minutos), muito depois de o proxy da nuvem já ter desistido.
_connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    _connect_args = {
        "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 3,
    }

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=_connect_args,
    # Descarta conexão morta (o pooler e o NAT da nuvem derrubam conexões ociosas).
    pool_pre_ping=True,
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "300")),
    # Plano gratuito: poucas conexões bastam e o Supabase limita o total.
    pool_size=int(os.getenv("DB_POOL_SIZE", "3")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "2")),
    pool_timeout=10,
)


if DATABASE_URL.startswith("postgresql"):
    _STATEMENT_TIMEOUT_MS = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "5000"))

    @event.listens_for(engine, "connect")
    def _limitar_consultas(dbapi_conn, _registro) -> None:
        # Consulta presa não pode prender a checagem inteira. Vai por SET e não pelo
        # parâmetro `options` da conexão porque poolers (PgBouncer/Supavisor) recusam
        # parâmetros de inicialização desconhecidos.
        with dbapi_conn.cursor() as cur:
            cur.execute(f"SET statement_timeout = {_STATEMENT_TIMEOUT_MS}")
        dbapi_conn.commit()


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