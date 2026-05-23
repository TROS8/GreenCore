import uuid
import requests
from conftest import skip_if_offline


@skip_if_offline
def test_get_all_zonas(base_url, auth):
    r = requests.get(f"{base_url}/zonas", headers=auth)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@skip_if_offline
def test_create_zona(base_url, auth):
    payload = {
        "nombre": f"Zona-{uuid.uuid4().hex[:8]}",
        "descripcion": "Test",
        "capacidadMaxima": 50,
        "temperaturaMinima": 15.0,
        "temperaturaMaxima": 30.0,
        "humedadMinima": 40.0,
        "humedadMaxima": 80.0,
        "activa": True,
    }
    r = requests.post(f"{base_url}/zonas", json=payload, headers=auth)
    assert r.status_code == 201
    assert "id" in r.json()


@skip_if_offline
def test_get_zona_by_id(base_url, auth):
    payload = {
        "nombre": f"Zona-{uuid.uuid4().hex[:8]}",
        "capacidadMaxima": 20,
        "temperaturaMinima": 10.0,
        "temperaturaMaxima": 25.0,
        "humedadMinima": 30.0,
        "humedadMaxima": 70.0,
        "activa": True,
    }
    zona_id = requests.post(f"{base_url}/zonas", json=payload, headers=auth).json()["id"]
    r = requests.get(f"{base_url}/zonas/{zona_id}", headers=auth)
    assert r.status_code == 200
    assert r.json()["id"] == zona_id


@skip_if_offline
def test_get_zona_not_found(base_url, auth):
    r = requests.get(f"{base_url}/zonas/999999", headers=auth)
    assert r.status_code == 404


@skip_if_offline
def test_delete_zona(base_url, auth):
    payload = {
        "nombre": f"Zona-{uuid.uuid4().hex[:8]}",
        "capacidadMaxima": 10,
        "temperaturaMinima": 10.0,
        "temperaturaMaxima": 25.0,
        "humedadMinima": 30.0,
        "humedadMaxima": 70.0,
        "activa": True,
    }
    zona_id = requests.post(f"{base_url}/zonas", json=payload, headers=auth).json()["id"]
    r = requests.delete(f"{base_url}/zonas/{zona_id}", headers=auth)
    assert r.status_code == 204


@skip_if_offline
def test_unauthorized_returns_401(base_url):
    r = requests.get(f"{base_url}/zonas")
    assert r.status_code == 401
