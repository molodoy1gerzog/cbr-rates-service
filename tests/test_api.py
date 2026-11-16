import httpx
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "broken"

def test_rates_returns_502_when_source_unavailable(monkeypatch):
    def fake_get(*args, **kwargs):
        raise httpx.ConnectError("source is down")

    monkeypatch.setattr(main.httpx, "get", fake_get)

    response = client.get("/rates")

    assert response.status_code == 502