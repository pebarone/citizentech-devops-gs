import importlib

import pytest
from fastapi.testclient import TestClient


def _client(monkeypatch, **env) -> TestClient:
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import citizentech.main as main

    importlib.reload(main)
    return TestClient(main.app)


@pytest.fixture
def client(monkeypatch):
    return _client(monkeypatch, METRICS_TOKEN="", ENABLE_CHAOS="false")


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_index_and_security_headers(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "CitizenTech" in r.text
    assert r.headers["X-Content-Type-Options"] == "nosniff"


def test_info(client):
    r = client.get("/api/v1/info")
    assert r.status_code == 200
    assert {"name", "environment", "version"} <= r.json().keys()


def test_metrics_exposes_golden_signals(client):
    client.get("/healthz")
    body = client.get("/metrics").text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert "http_requests_in_progress" in body


def test_metrics_requires_token_when_configured(monkeypatch):
    c = _client(monkeypatch, METRICS_TOKEN="token-de-teste")
    assert c.get("/metrics").status_code == 401
    assert c.get("/metrics", headers={"Authorization": "Bearer errado"}).status_code == 401
    assert c.get("/metrics", headers={"Authorization": "Bearer token-de-teste"}).status_code == 200


def test_chaos_disabled_by_default(client):
    assert client.get("/api/v1/chaos/error").status_code == 404


def test_chaos_error_when_enabled(monkeypatch):
    c = _client(monkeypatch, ENABLE_CHAOS="true")
    assert c.get("/api/v1/chaos/error").status_code == 500
