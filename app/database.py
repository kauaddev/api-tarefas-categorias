import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tarefas.db")

# check_same_thread só é necessário para SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe base de todos os modelos ORM."""


def get_db():
    """Dependência do FastAPI: abre e fecha uma sessão por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
