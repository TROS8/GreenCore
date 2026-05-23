import requests
from conftest import skip_if_offline


@skip_if_offline
def test_get_all_usuarios(base_url, auth):
    r = requests.get(f"{base_url}/usuarios", headers=auth)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@skip_if_offline
def test_get_usuario_not_found(base_url, auth):
    assert requests.get(f"{base_url}/usuarios/999999", headers=auth).status_code == 404


@skip_if_offline
def test_unauthorized_returns_401(base_url):
    assert requests.get(f"{base_url}/usuarios").status_code == 401
