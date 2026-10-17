def test_listar_categorias_vazio_retorna_200(client):
    r = client.get("/categorias")
    assert r.status_code == 200
    assert r.json() == []


def test_criar_categoria_sem_token_retorna_401(client):
    r = client.post("/categorias", json={"nome": "Estudos"})
    assert r.status_code == 401


def test_criar_categoria_retorna_201(client, auth):
    r = client.post("/categorias", json={"nome": "Trabalho"}, headers=auth)
    assert r.status_code == 201
    assert r.json() == {"id": 1, "nome": "Trabalho"}


def test_criar_categoria_duplicada_retorna_409(client, auth, categoria):
    r = client.post("/categorias", json={"nome": "Estudos"}, headers=auth)
    assert r.status_code == 409


def test_criar_categoria_com_nome_vazio_retorna_400(client, auth):
    r = client.post("/categorias", json={"nome": ""}, headers=auth)
    assert r.status_code == 400


def test_consultar_categoria_existente_retorna_200(client, categoria):
    r = client.get(f"/categorias/{categoria['id']}")
    assert r.status_code == 200
    assert r.json()["nome"] == "Estudos"


def test_consultar_categoria_inexistente_retorna_404(client):
    assert client.get("/categorias/999").status_code == 404


def test_atualizar_categoria_retorna_200(client, auth, categoria):
    r = client.patch(f"/categorias/{categoria['id']}", json={"nome": "Faculdade"}, headers=auth)
    assert r.status_code == 200
    assert r.json()["nome"] == "Faculdade"


def test_atualizar_categoria_para_nome_ja_usado_retorna_409(client, auth, categoria):
    client.post("/categorias", json={"nome": "Casa"}, headers=auth)
    r = client.patch("/categorias/2", json={"nome": "Estudos"}, headers=auth)
    assert r.status_code == 409


def test_atualizar_categoria_inexistente_retorna_404(client, auth):
    r = client.patch("/categorias/999", json={"nome": "X"}, headers=auth)
    assert r.status_code == 404


def test_excluir_categoria_retorna_204_e_some(client, auth, categoria):
    r = client.delete(f"/categorias/{categoria['id']}", headers=auth)
    assert r.status_code == 204
    assert client.get(f"/categorias/{categoria['id']}").status_code == 404


def test_excluir_categoria_inexistente_retorna_404(client, auth):
    assert client.delete("/categorias/999", headers=auth).status_code == 404


def test_excluir_categoria_com_tarefas_retorna_409(client, auth, tarefa):
    r = client.delete(f"/categorias/{tarefa['categoria_id']}", headers=auth)
    assert r.status_code == 409


def test_excluir_categoria_sem_token_retorna_401(client, categoria):
    assert client.delete(f"/categorias/{categoria['id']}").status_code == 401
