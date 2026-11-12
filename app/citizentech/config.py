"""Configuração lida só de variáveis de ambiente. Nenhum segredo fica no código."""

import os
from dataclasses import dataclass


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    # Versão da imagem (SHA do commit), injetada pelo pipeline no deploy.
    version: str
    # Token exigido em /metrics. Vazio = /metrics aberto (só para uso local).
    metrics_token: str
    # Habilita /api/v1/chaos/* para demonstrar o alerta. Nunca ligar sem necessidade.
    enable_chaos: bool


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Alerta Córrego"),
        environment=os.getenv("APP_ENV", "local"),
        version=os.getenv("APP_VERSION", "dev"),
        metrics_token=os.getenv("METRICS_TOKEN", ""),
        enable_chaos=_bool("ENABLE_CHAOS"),
    )
