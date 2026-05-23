import uuid
import requests
from conftest import skip_if_offline


def _create_zona(base_url, auth):
    payload = {
        "nombre": f"ZPlt-{uuid.uuid4().hex[:8]}",
        "capacidadMaxima": 100,
        "temperaturaMinima": 15.0,
        "temperaturaMaxima": 28.0,
        "humedadMinima": 50.0,
        "humedadMaxima": 85.0,
        "activa": True,
    }
    return requests.post(f"{base_url}/zonas", json=payload, headers=auth).json()["id"]


@skip_if_offline
def test_get_all_plantas(base_url, auth):
    r = requests.get(f"{base_url}/plantas", headers=auth)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@skip_if_offline
def test_create_planta(base_url, auth):
    zona_id = _create_zona(base_url, auth)
    payload = {
        "nombre": "Tomate Cherry",
        "especie": "Solanum lycopersicum",
        "lote": f"LOT-{uuid.uuid4().hex[:8]}",
        "cantidad": 100,
        "precio": 2.50,
        "estado": "SEMILLA",
        "fechaSiembra": "2026-01-15",
        "zona": {"id": zona_id},
    }
    r = requests.post(f"{base_url}/plantas", json=payload, headers=auth)
    assert r.status_code == 201
    assert "id" in r.json()


@skip_if_offline
def test_get_planta_by_id(base_url, auth):
    zona_id = _create_zona(base_url, auth)
    payload = {
        "nombre": "Menta",
        "especie": "Mentha",
        "lote": f"LOT-{uuid.uuid4().hex[:8]}",
        "cantidad": 20,
        "precio": 1.00,
        "estado": "SEMILLA",
        "fechaSiembra": "2026-02-01",
        "zona": {"id": zona_id},
    }
    pid = requests.post(f"{base_url}/plantas", json=payload, headers=auth).json()["id"]
    r = requests.get(f"{base_url}/plantas/{pid}", headers=auth)
    assert r.status_code == 200


@skip_if_offline
def test_get_planta_not_found(base_url, auth):
    assert requests.get(f"{base_url}/plantas/999999", headers=auth).status_code == 404


@skip_if_offline
def test_unauthorized_returns_401(base_url):
    assert requests.get(f"{base_url}/plantas").status_code == 401
