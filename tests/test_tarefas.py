# ---------- GET (listagem e consulta) ----------
def test_listar_tarefas_vazio_retorna_200(client):
    r = client.get("/tarefas")
    assert r.status_code == 200
    assert r.json() == []


def test_listar_tarefas_e_publico_e_retorna_a_tarefa(client, tarefa):
    r = client.get("/tarefas")  # sem token
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_consultar_tarefa_existente_retorna_200(client, tarefa):
    r = client.get(f"/tarefas/{tarefa['id']}")
    assert r.status_code == 200
    assert r.json()["titulo"] == "Entregar trabalho de APIs"


def test_consultar_tarefa_inexistente_retorna_404(client):
    r = client.get("/tarefas/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Tarefa não encontrada"


def test_consultar_tarefa_com_id_nao_numerico_retorna_400(client):
    assert client.get("/tarefas/abc").status_code == 400


# ---------- Filtros ----------
def test_filtrar_por_concluida(client, auth, tarefa):
    client.post("/tarefas", json={"titulo": "Já feita", "concluida": True}, headers=auth)
    feitas = client.get("/tarefas?concluida=true").json()
    pendentes = client.get("/tarefas?concluida=false").json()
    assert [t["titulo"] for t in feitas] == ["Já feita"]
    assert [t["titulo"] for t in pendentes] == ["Entregar trabalho de APIs"]


def test_filtrar_por_categoria(client, auth, tarefa):
    client.post("/tarefas", json={"titulo": "Sem categoria"}, headers=auth)
    r = client.get(f"/tarefas?categoria_id={tarefa['categoria_id']}")
    assert [t["titulo"] for t in r.json()] == ["Entregar trabalho de APIs"]


def test_buscar_por_texto_ignora_maiusculas(client, tarefa):
    assert len(client.get("/tarefas?busca=APIS").json()) == 1
    assert client.get("/tarefas?busca=inexistente").json() == []


# ---------- POST ----------
def test_criar_tarefa_sem_token_retorna_401(client):
    assert client.post("/tarefas", json={"titulo": "X"}).status_code == 401


def test_criar_tarefa_retorna_201_com_valores_padrao(client, auth):
    r = client.post("/tarefas", json={"titulo": "Estudar FastAPI"}, headers=auth)
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["id"] == 1
    assert corpo["concluida"] is False
    assert corpo["categoria_id"] is None
    assert corpo["criada_em"]


def test_criar_tarefa_sem_titulo_retorna_400(client, auth):
    r = client.post("/tarefas", json={}, headers=auth)
    assert r.status_code == 400
    assert r.json()["erros"][0]["campo"] == "titulo"


def test_criar_tarefa_com_titulo_vazio_retorna_400(client, auth):
    assert client.post("/tarefas", json={"titulo": ""}, headers=auth).status_code == 400


def test_criar_tarefa_com_titulo_longo_demais_retorna_400(client, auth):
    r = client.post("/tarefas", json={"titulo": "x" * 121}, headers=auth)
    assert r.status_code == 400


def test_criar_tarefa_com_tipo_errado_retorna_400(client, auth):
    r = client.post("/tarefas", json={"titulo": "X", "concluida": "talvez"}, headers=auth)
    assert r.status_code == 400


def test_criar_tarefa_com_categoria_inexistente_retorna_400(client, auth):
    r = client.post("/tarefas", json={"titulo": "X", "categoria_id": 999}, headers=auth)
    assert r.status_code == 400


# ---------- PATCH ----------
def test_atualizar_parcialmente_preserva_os_outros_campos(client, auth, tarefa):
    r = client.patch(f"/tarefas/{tarefa['id']}", json={"concluida": True}, headers=auth)
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["concluida"] is True
    assert corpo["titulo"] == tarefa["titulo"]
    assert corpo["descricao"] == tarefa["descricao"]
    assert corpo["categoria_id"] == tarefa["categoria_id"]


def test_atualizacao_e_persistida_no_banco(client, auth, tarefa):
    client.patch(f"/tarefas/{tarefa['id']}", json={"titulo": "Novo título"}, headers=auth)
    assert client.get(f"/tarefas/{tarefa['id']}").json()["titulo"] == "Novo título"


def test_remover_categoria_da_tarefa_com_null(client, auth, tarefa):
    r = client.patch(f"/tarefas/{tarefa['id']}", json={"categoria_id": None}, headers=auth)
    assert r.status_code == 200
    assert r.json()["categoria_id"] is None


def test_atualizar_titulo_vazio_retorna_400(client, auth, tarefa):
    r = client.patch(f"/tarefas/{tarefa['id']}", json={"titulo": ""}, headers=auth)
    assert r.status_code == 400


def test_atualizar_titulo_para_null_retorna_400(client, auth, tarefa):
    r = client.patch(f"/tarefas/{tarefa['id']}", json={"titulo": None}, headers=auth)
    assert r.status_code == 400


def test_atualizar_com_categoria_inexistente_retorna_400(client, auth, tarefa):
    r = client.patch(f"/tarefas/{tarefa['id']}", json={"categoria_id": 0}, headers=auth)
    assert r.status_code == 400


def test_atualizar_tarefa_inexistente_retorna_404(client, auth):
    r = client.patch("/tarefas/999", json={"concluida": True}, headers=auth)
    assert r.status_code == 404


def test_atualizar_tarefa_sem_token_retorna_401(client, tarefa):
    r = client.patch(f"/tarefas/{tarefa['id']}", json={"concluida": True})
    assert r.status_code == 401


# ---------- DELETE ----------
def test_excluir_tarefa_retorna_204_e_ela_some(client, auth, tarefa):
    r = client.delete(f"/tarefas/{tarefa['id']}", headers=auth)
    assert r.status_code == 204
    assert r.content == b""
    assert client.get(f"/tarefas/{tarefa['id']}").status_code == 404


def test_excluir_tarefa_duas_vezes_retorna_404_na_segunda(client, auth, tarefa):
    client.delete(f"/tarefas/{tarefa['id']}", headers=auth)
    assert client.delete(f"/tarefas/{tarefa['id']}", headers=auth).status_code == 404


def test_excluir_tarefa_sem_token_retorna_401(client, tarefa):
    assert client.delete(f"/tarefas/{tarefa['id']}").status_code == 401
