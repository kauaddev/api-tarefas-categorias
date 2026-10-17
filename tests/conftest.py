"""Configuração compartilhada dos testes.

Cada teste roda contra um banco SQLite em memória, novo e vazio. Assim os testes
não dependem uns dos outros e NUNCA tocam no seu tarefas.db real.
"""
import os

# Estas variáveis precisam existir ANTES de importar a aplicação
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "chave-usada-somente-nos-testes"
os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://localhost:5173"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

USUARIO = {"username": "aluno", "senha": "senha-forte-123"}


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # mantém o mesmo banco em memória entre conexões
    )
    Base.metadata.create_all(engine)
    Sessao = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def get_db_teste():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_teste
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture()
def auth(client):
    """Cabeçalho Authorization de um usuário já registrado e logado."""
    client.post("/auth/registrar", json=USUARIO)
    r = client.post(
        "/auth/login", data={"username": USUARIO["username"], "password": USUARIO["senha"]}
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def categoria(client, auth):
    """Uma categoria já criada (id 1)."""
    r = client.post("/categorias", json={"nome": "Estudos"}, headers=auth)
    assert r.status_code == 201
    return r.json()


@pytest.fixture()
def tarefa(client, auth, categoria):
    """Uma tarefa já criada (id 1) dentro da categoria Estudos."""
    r = client.post(
        "/tarefas",
        json={"titulo": "Entregar trabalho de APIs", "descricao": "Atividade prática",
              "categoria_id": categoria["id"]},
        headers=auth,
    )
    assert r.status_code == 201
    return r.json()
