import uuid
import requests
from conftest import skip_if_offline


@skip_if_offline
def test_get_all_clientes(base_url, auth):
    r = requests.get(f"{base_url}/clientes", headers=auth)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@skip_if_offline
def test_create_cliente(base_url, auth):
    payload = {
        "nombre": "Cliente Test",
        "email": f"cli-{uuid.uuid4().hex[:8]}@test.com",
        "telefono": "555-0100",
        "ciudad": "Lima",
        "activo": True,
    }
    r = requests.post(f"{base_url}/clientes", json=payload, headers=auth)
    assert r.status_code == 201
    assert "id" in r.json()


@skip_if_offline
def test_get_cliente_by_id(base_url, auth):
    payload = {"nombre": "Get", "email": f"get-{uuid.uuid4().hex[:8]}@test.com", "activo": True}
    cid = requests.post(f"{base_url}/clientes", json=payload, headers=auth).json()["id"]
    r = requests.get(f"{base_url}/clientes/{cid}", headers=auth)
    assert r.status_code == 200
    assert r.json()["id"] == cid


@skip_if_offline
def test_get_cliente_not_found(base_url, auth):
    assert requests.get(f"{base_url}/clientes/999999", headers=auth).status_code == 404


@skip_if_offline
def test_delete_cliente(base_url, auth):
    payload = {"nombre": "Del", "email": f"del-{uuid.uuid4().hex[:8]}@test.com", "activo": True}
    cid = requests.post(f"{base_url}/clientes", json=payload, headers=auth).json()["id"]
    assert requests.delete(f"{base_url}/clientes/{cid}", headers=auth).status_code == 204


@skip_if_offline
def test_unauthorized_returns_401(base_url):
    assert requests.get(f"{base_url}/clientes").status_code == 401
