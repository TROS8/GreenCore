"""
Shared fixtures for Python API integration tests.
Tests are skipped automatically when the backend is not running.
"""
import os
import pytest
import requests

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8080/api/v1")
JWT_SECRET = os.getenv("JWT_SECRET", "greencore-super-secret-key-2026-local")


def _backend_running() -> bool:
    try:
        requests.get(f"{BASE_URL}/zonas", timeout=2)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


skip_if_offline = pytest.mark.skipif(
    not _backend_running(),
    reason="Backend not reachable at " + BASE_URL,
)


def _make_token() -> str:
    from datetime import datetime, timedelta, timezone
    import jwt as pyjwt

    payload = {
        "sub": "pytest@greencore.test",
        "role": "ADMIN",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def auth(base_url) -> dict:
    """Returns Authorization header dict for every authenticated request."""
    return {"Authorization": f"Bearer {_make_token()}"}
