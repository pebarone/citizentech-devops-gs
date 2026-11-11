"""Métricas Prometheus para os 4 sinais de ouro.

- Latência: histograma http_request_duration_seconds
- Tráfego:  contador http_requests_total
- Erros:    http_requests_total com status 5xx
- Saturação: http_requests_in_progress + métricas de processo (CPU, memória)
"""

import time

from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.routing import Match

REQUESTS = Counter(
    "http_requests_total",
    "Total de requisições HTTP",
    ["method", "route", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Latência das requisições HTTP",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)
IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Requisições HTTP em andamento",
)

_IGNORED = {"/metrics"}


def _route_template(request: Request) -> str:
    """Usa o template da rota (ex.: /api/v1/itens/{id}) para não explodir a cardinalidade."""
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            return getattr(route, "path", request.url.path)
    return "unmatched"


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        route = _route_template(request)
        if route in _IGNORED:
            return await call_next(request)

        IN_PROGRESS.inc()
        start = time.perf_counter()
        status = "500"
        try:
            response = await call_next(request)
            status = str(response.status_code)
            return response
        finally:
            LATENCY.labels(request.method, route).observe(time.perf_counter() - start)
            REQUESTS.labels(request.method, route, status).inc()
            IN_PROGRESS.dec()
