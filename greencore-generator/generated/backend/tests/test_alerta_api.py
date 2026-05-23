import requests

BASE_URL = "http://localhost:8080/api/v1"


def test_get_all_alertas():
    response = requests.get(f"{BASE_URL}/alertas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)