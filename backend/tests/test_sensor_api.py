import uuid
import requests
from conftest import skip_if_offline


def _create_zona(base_url, auth):
    payload = {
        "nombre": f"ZSen-{uuid.uuid4().hex[:8]}",
        "capacidadMaxima": 30,
        "temperaturaMinima": 10.0,
        "temperaturaMaxima": 35.0,
        "humedadMinima": 30.0,
        "humedadMaxima": 90.0,
        "activa": True,
    }
    return requests.post(f"{base_url}/zonas", json=payload, headers=auth).json()["id"]


@skip_if_offline
def test_get_all_sensors(base_url, auth):
    r = requests.get(f"{base_url}/sensores", headers=auth)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@skip_if_offline
def test_create_sensor(base_url, auth):
    zona_id = _create_zona(base_url, auth)
    payload = {
        "codigo": f"SEN-{uuid.uuid4().hex[:8]}",
        "tipo": "TEMPERATURA",
        "unidad": "°C",
        "umbralMinimo": 10.0,
        "umbralMaximo": 40.0,
        "estado": "ACTIVO",
        "zona": {"id": zona_id},
    }
    r = requests.post(f"{base_url}/sensores", json=payload, headers=auth)
    assert r.status_code == 201
    assert "id" in r.json()


@skip_if_offline
def test_registrar_lectura(base_url, auth):
    zona_id = _create_zona(base_url, auth)
    sensor_payload = {
        "codigo": f"SEN-{uuid.uuid4().hex[:8]}",
        "tipo": "HUMEDAD",
        "unidad": "%",
        "umbralMinimo": 30.0,
        "umbralMaximo": 80.0,
        "estado": "ACTIVO",
        "zona": {"id": zona_id},
    }
    sensor_id = requests.post(f"{base_url}/sensores", json=sensor_payload, headers=auth).json()["id"]
    r = requests.post(f"{base_url}/sensores/{sensor_id}/lectura", json={"valor": 55.0}, headers=auth)
    assert r.status_code == 201
    assert r.json()["fueraDeRango"] is False


@skip_if_offline
def test_get_sensor_not_found(base_url, auth):
    assert requests.get(f"{base_url}/sensores/999999", headers=auth).status_code == 404


@skip_if_offline
def test_unauthorized_returns_401(base_url):
    assert requests.get(f"{base_url}/sensores").status_code == 401
