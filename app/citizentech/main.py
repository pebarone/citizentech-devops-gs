"""Ponto de entrada da API do MVP.

Esqueleto de produção: saúde, informações, métricas e página estática.
As rotas de negócio da CitizenTech entram em /api/v1 conforme o produto for definido.
"""

import asyncio
import hmac
import random
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import FileResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from . import __version__
from .config import get_settings
from .metrics import PrometheusMiddleware

STATIC_DIR = Path(__file__).parent / "static"

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=__version__,
    # Documentação interativa só fora de produção.
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None,
    openapi_url=None if settings.environment == "production" else "/openapi.json",
)
app.add_middleware(PrometheusMiddleware)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Frame-Options", "DENY")
    return response


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz", tags=["ops"])
def healthz() -> dict:
    """Liveness: o processo está de pé."""
    return {"status": "ok"}


@app.get("/readyz", tags=["ops"])
def readyz() -> dict:
    """Readiness: pronto para receber tráfego. Incluir aqui a checagem de dependências (banco, fila)."""
    return {"status": "ready"}


@app.get("/api/v1/info", tags=["mvp"])
def info() -> dict:
    return {
        "name": settings.app_name,
        "environment": settings.environment,
        "version": settings.version,
    }


@app.get("/metrics", include_in_schema=False)
def metrics(authorization: str | None = Header(default=None)) -> Response:
    if settings.metrics_token:
        expected = f"Bearer {settings.metrics_token}"
        if not authorization or not hmac.compare_digest(authorization, expected):
            raise HTTPException(status_code=401, detail="unauthorized")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# --- Demonstração do alerta (desligado por padrão) -------------------------------

@app.get("/api/v1/chaos/error", tags=["chaos"], include_in_schema=False)
def chaos_error() -> dict:
    """Devolve 500 para disparar o alerta de taxa de erro. Exige ENABLE_CHAOS=true."""
    if not settings.enable_chaos:
        raise HTTPException(status_code=404)
    raise HTTPException(status_code=500, detail="erro simulado")


@app.get("/api/v1/chaos/slow", tags=["chaos"], include_in_schema=False)
async def chaos_slow() -> dict:
    """Responde devagar para disparar o alerta de latência. Exige ENABLE_CHAOS=true."""
    if not settings.enable_chaos:
        raise HTTPException(status_code=404)
    delay = random.uniform(1.5, 3.0)  # nosec B311 - não é uso criptográfico
    await asyncio.sleep(delay)
    return {"slept_seconds": round(delay, 2)}
