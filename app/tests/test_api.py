import importlib
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from citizentech.corregos import leituras

RISCOS = {"normal", "atencao", "alerta", "emergencia"}
CAMPOS_LEITURA = {"id", "nome", "bairro", "nivel_cm", "chuva_mm_1h", "risco", "orientacao", "atualizado_em", "fonte"}


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
    assert "Alerta Córrego" in r.text
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


def test_corregos_lista_quatro_pontos(client):
    r = client.get("/api/v1/corregos")
    assert r.status_code == 200
    body = r.json()
    assert {"atualizado_em", "fonte", "pontos"} <= body.keys()
    assert body["fonte"] == "simulado"
    assert len(body["pontos"]) == 4
    for ponto in body["pontos"]:
        assert CAMPOS_LEITURA <= ponto.keys()
        assert ponto["risco"] in RISCOS
        assert isinstance(ponto["nivel_cm"], int)
        assert isinstance(ponto["chuva_mm_1h"], float)
        assert ponto["fonte"] == "simulado"


def test_corrego_por_id(client):
    r = client.get("/api/v1/corregos/itaquera-pantanal")
    assert r.status_code == 200
    assert r.json()["id"] == "itaquera-pantanal"
    assert client.get("/api/v1/corregos/xyz").status_code == 404


def test_leituras_sao_deterministicas_no_mesmo_minuto():
    agora = datetime(2026, 11, 11, 15, 30, 5, tzinfo=timezone.utc)
    assert leituras(agora) == leituras(agora)

    def valores(instante):
        return [{k: v for k, v in p.items() if k != "atualizado_em"} for p in leituras(instante)]

    assert valores(agora) == valores(agora.replace(second=50))


def test_leituras_ciclo_de_3_horas_tem_normal_e_alerta_em_cada_ponto():
    inicio = datetime(2026, 11, 11, 0, 0, tzinfo=timezone.utc)
    riscos: dict[str, set[str]] = {}
    for minutos in range(0, 3 * 60 + 1, 5):
        for ponto in leituras(inicio + timedelta(minutes=minutos)):
            riscos.setdefault(ponto["id"], set()).add(ponto["risco"])
    assert len(riscos) == 4
    for ponto_id, conjunto in riscos.items():
        assert "normal" in conjunto, ponto_id
        assert conjunto & {"alerta", "emergencia"}, ponto_id


def test_metrics_rotula_rota_pelo_template(client):
    client.get("/api/v1/corregos/itaquera-pantanal")
    body = client.get("/metrics").text
    assert 'route="/api/v1/corregos/{ponto_id}"' in body
    assert 'route="/api/v1/corregos/itaquera-pantanal"' not in body
