PERMITIDA = "http://localhost:3000"
NAO_PERMITIDA = "http://site-malicioso.com"


def preflight(client, origem, metodo="POST"):
    return client.options(
        "/tarefas",
        headers={
            "Origin": origem,
            "Access-Control-Request-Method": metodo,
            "Access-Control-Request-Headers": "authorization",
        },
    )


def test_preflight_de_origem_permitida_e_aceito(client):
    r = preflight(client, PERMITIDA)
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == PERMITIDA
    assert "PATCH" in r.headers["access-control-allow-methods"]


def test_preflight_de_origem_nao_permitida_e_rejeitado(client):
    r = preflight(client, NAO_PERMITIDA)
    assert r.status_code == 400
    assert "access-control-allow-origin" not in r.headers


def test_preflight_com_metodo_nao_permitido_e_rejeitado(client):
    r = preflight(client, PERMITIDA, metodo="PUT")
    assert r.status_code == 400


def test_resposta_para_origem_permitida_traz_cabecalho_cors(client):
    r = client.get("/tarefas", headers={"Origin": PERMITIDA})
    assert r.headers["access-control-allow-origin"] == PERMITIDA


def test_resposta_para_origem_nao_permitida_nao_traz_cabecalho_cors(client):
    r = client.get("/tarefas", headers={"Origin": NAO_PERMITIDA})
    assert "access-control-allow-origin" not in r.headers
