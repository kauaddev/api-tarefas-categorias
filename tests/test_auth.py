from datetime import datetime, timedelta, timezone

import jwt

from app import config
from tests.conftest import USUARIO


def login(client, username=USUARIO["username"], senha=USUARIO["senha"]):
    return client.post("/auth/login", data={"username": username, "password": senha})


def test_registrar_usuario_retorna_201_sem_expor_senha(client):
    r = client.post("/auth/registrar", json=USUARIO)
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["username"] == "aluno"
    assert "senha" not in corpo and "senha_hash" not in corpo


def test_registrar_usuario_duplicado_retorna_409(client):
    client.post("/auth/registrar", json=USUARIO)
    r = client.post("/auth/registrar", json=USUARIO)
    assert r.status_code == 409


def test_registrar_senha_curta_retorna_400(client):
    r = client.post("/auth/registrar", json={"username": "aluno2", "senha": "curta"})
    assert r.status_code == 400
    assert r.json()["erros"][0]["campo"] == "senha"


def test_registrar_username_com_caracteres_invalidos_retorna_400(client):
    r = client.post("/auth/registrar", json={"username": "alu no!", "senha": "senha-forte-123"})
    assert r.status_code == 400


def test_login_correto_retorna_token_bearer(client):
    client.post("/auth/registrar", json=USUARIO)
    r = login(client)
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_login_com_senha_errada_retorna_401(client):
    client.post("/auth/registrar", json=USUARIO)
    r = login(client, senha="senha-errada-999")
    assert r.status_code == 401


def test_login_usuario_inexistente_retorna_401_com_mesma_mensagem(client):
    client.post("/auth/registrar", json=USUARIO)
    senha_errada = login(client, senha="senha-errada-999")
    inexistente = login(client, username="fantasma")
    assert inexistente.status_code == 401
    # a API não revela se foi o usuário ou a senha que falhou
    assert inexistente.json() == senha_errada.json()


def test_endpoint_protegido_sem_token_retorna_401(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_endpoint_protegido_com_token_valido_retorna_200(client, auth):
    r = client.get("/auth/me", headers=auth)
    assert r.status_code == 200
    assert r.json()["username"] == "aluno"


def test_token_invalido_retorna_401(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer token.falso.qualquer"})
    assert r.status_code == 401


def test_token_expirado_retorna_401(client):
    client.post("/auth/registrar", json=USUARIO)
    expirado = jwt.encode(
        {"sub": "aluno", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        config.SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {expirado}"})
    assert r.status_code == 401


def test_token_assinado_com_outra_chave_retorna_401(client):
    client.post("/auth/registrar", json=USUARIO)
    falso = jwt.encode(
        {"sub": "aluno", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "outra-chave-qualquer-com-32-bytes-ou-mais!!",
        algorithm=config.JWT_ALGORITHM,
    )
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {falso}"})
    assert r.status_code == 401
