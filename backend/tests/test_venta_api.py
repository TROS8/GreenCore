import uuid
import requests
from conftest import skip_if_offline


def _create_planta_with_zona(base_url, auth):
    zona = {
        "nombre": f"ZVen-{uuid.uuid4().hex[:8]}",
        "capacidadMaxima": 50,
        "temperaturaMinima": 12.0,
        "temperaturaMaxima": 28.0,
        "humedadMinima": 40.0,
        "humedadMaxima": 75.0,
        "activa": True,
    }
    zona_id = requests.post(f"{base_url}/zonas", json=zona, headers=auth).json()["id"]
    planta = {
        "nombre": "Albahaca",
        "especie": "Ocimum basilicum",
        "lote": f"LOT-{uuid.uuid4().hex[:8]}",
        "cantidad": 50,
        "precio": 1.80,
        "estado": "LISTO_VENTA",
        "fechaSiembra": "2026-01-01",
        "zona": {"id": zona_id},
    }
    return requests.post(f"{base_url}/plantas", json=planta, headers=auth).json()["id"]


def _create_cliente(base_url, auth):
    payload = {"nombre": "CV", "email": f"cv-{uuid.uuid4().hex[:8]}@test.com", "activo": True}
    return requests.post(f"{base_url}/clientes", json=payload, headers=auth).json()["id"]


@skip_if_offline
def test_get_all_ventas(base_url, auth):
    r = requests.get(f"{base_url}/ventas", headers=auth)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@skip_if_offline
def test_create_venta(base_url, auth):
    payload = {
        "numeroFactura": f"FAC-{uuid.uuid4().hex[:8]}",
        "cantidad": 10,
        "precioUnitario": 1.80,
        "total": 18.00,
        "estado": "PENDIENTE",
        "fecha": "2026-05-01T10:00:00",
        "planta": {"id": _create_planta_with_zona(base_url, auth)},
        "cliente": {"id": _create_cliente(base_url, auth)},
    }
    r = requests.post(f"{base_url}/ventas", json=payload, headers=auth)
    assert r.status_code == 201
    assert "id" in r.json()


@skip_if_offline
def test_get_venta_not_found(base_url, auth):
    assert requests.get(f"{base_url}/ventas/999999", headers=auth).status_code == 404


@skip_if_offline
def test_unauthorized_returns_401(base_url):
    assert requests.get(f"{base_url}/ventas").status_code == 401
