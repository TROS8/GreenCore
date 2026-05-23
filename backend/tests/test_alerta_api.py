import uuid
import requests
from conftest import skip_if_offline


def _create_sensor_out_of_range(base_url, auth):
    zona = {
        "nombre": f"ZAlt-{uuid.uuid4().hex[:8]}",
        "capacidadMaxima": 20,
        "temperaturaMinima": 10.0,
        "temperaturaMaxima": 30.0,
        "humedadMinima": 40.0,
        "humedadMaxima": 80.0,
        "activa": True,
    }
    zona_id = requests.post(f"{base_url}/zonas", json=zona, headers=auth).json()["id"]
    sensor = {
        "codigo": f"SEN-ALT-{uuid.uuid4().hex[:8]}",
        "tipo": "TEMPERATURA",
        "unidad": "°C",
        "umbralMinimo": 15.0,
        "umbralMaximo": 25.0,
        "estado": "ACTIVO",
        "zona": {"id": zona_id},
    }
    sensor_id = requests.post(f"{base_url}/sensores", json=sensor, headers=auth).json()["id"]
    # Post a value above the maximum threshold to trigger an alerta
    requests.post(f"{base_url}/sensores/{sensor_id}/lectura", json={"valor": 50.0}, headers=auth)


@skip_if_offline
def test_get_all_alertas(base_url, auth):
    r = requests.get(f"{base_url}/alertas", headers=auth)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@skip_if_offline
def test_out_of_range_lectura_generates_alerta(base_url, auth):
    before = len(requests.get(f"{base_url}/alertas", headers=auth).json())
    _create_sensor_out_of_range(base_url, auth)
    after = len(requests.get(f"{base_url}/alertas", headers=auth).json())
    assert after > before


@skip_if_offline
def test_get_alerta_not_found(base_url, auth):
    assert requests.get(f"{base_url}/alertas/999999", headers=auth).status_code == 404


@skip_if_offline
def test_unauthorized_returns_401(base_url):
    assert requests.get(f"{base_url}/alertas").status_code == 401
