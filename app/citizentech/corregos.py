"""Alerta Córrego: pontos monitorados e leituras simuladas.

No MVP, o nível da água e a chuva são simulados a partir do horário, sem aleatoriedade:
o mesmo minuto sempre gera os mesmos valores. Os sensores físicos (ESP32 com sensor
ultrassônico) são outro componente e ainda não alimentam esta API.
"""

import math
from dataclasses import dataclass
from datetime import datetime, timezone

# Ciclo simulado da chuva, em minutos (3 horas).
CICLO_MINUTOS = 3 * 60
# Chuva máxima simulada na última hora, em mm.
CHUVA_MAXIMA_MM_1H = 30.0
# Quanto o nível simulado passa do limite de transbordo no pico, em cm.
FOLGA_PICO_CM = 10

ORIENTACOES = {
    "normal": "Sem risco no momento.",
    "atencao": "Fique atento e acompanhe as atualizações.",
    "alerta": "Separe documentos e remédios e prepare-se para sair.",
    "emergencia": "Saia agora para um local alto. Ligue 199 (Defesa Civil) ou 193 (Bombeiros).",
}


@dataclass(frozen=True)
class PontoMonitorado:
    id: str
    nome: str
    bairro: str
    nivel_normal_cm: int
    nivel_atencao_cm: int
    nivel_alerta_cm: int
    nivel_transbordo_cm: int


PONTOS: tuple[PontoMonitorado, ...] = (
    PontoMonitorado("itaquera-pantanal", "Córrego Itaquera", "Jardim Pantanal", 60, 120, 170, 210),
    PontoMonitorado("tres-pontes-helena", "Córrego Três Pontes", "Jardim Helena", 55, 115, 160, 200),
    PontoMonitorado("tiete-romano", "Rio Tietê (margem)", "Jardim Romano", 70, 130, 180, 220),
    PontoMonitorado("lajeado-guaianases", "Córrego Lajeado", "Guaianases", 65, 125, 175, 215),
)


def _utc(instante: datetime) -> datetime:
    """Datetime sem fuso é tratado como UTC."""
    if instante.tzinfo is None:
        instante = instante.replace(tzinfo=timezone.utc)
    return instante.astimezone(timezone.utc)


def iso_utc(instante: datetime) -> str:
    """Formata o instante em ISO 8601 UTC, por exemplo 2026-11-11T15:00:00Z."""
    return _utc(instante).strftime("%Y-%m-%dT%H:%M:%SZ")


def _classificar(nivel_cm: int, ponto: PontoMonitorado) -> str:
    if nivel_cm < ponto.nivel_atencao_cm:
        return "normal"
    if nivel_cm < ponto.nivel_alerta_cm:
        return "atencao"
    if nivel_cm < ponto.nivel_transbordo_cm:
        return "alerta"
    return "emergencia"


def _leitura(ponto: PontoMonitorado, indice: int, minutos: int, atualizado_em: str) -> dict:
    # Cada ponto tem uma fase própria do ciclo, então os níveis não sobem todos juntos.
    fase_ponto = 2 * math.pi * indice / len(PONTOS)
    fase_ciclo = 2 * math.pi * (minutos % CICLO_MINUTOS) / CICLO_MINUTOS
    onda = (1 + math.sin(fase_ciclo + fase_ponto)) / 2  # de 0 a 1
    intensidade = onda * onda
    nivel_cm = round(
        ponto.nivel_normal_cm
        + (ponto.nivel_transbordo_cm + FOLGA_PICO_CM - ponto.nivel_normal_cm) * intensidade
    )
    risco = _classificar(nivel_cm, ponto)
    return {
        "id": ponto.id,
        "nome": ponto.nome,
        "bairro": ponto.bairro,
        "nivel_cm": nivel_cm,
        "chuva_mm_1h": round(CHUVA_MAXIMA_MM_1H * intensidade, 1),
        "risco": risco,
        "orientacao": ORIENTACOES[risco],
        "atualizado_em": atualizado_em,
        "fonte": "simulado",
    }


def leituras(agora: datetime) -> list[dict]:
    """Leituras simuladas de todos os pontos monitorados.

    Os valores dependem só do minuto: segundos e microssegundos não mudam o resultado.
    """
    instante = _utc(agora)
    minutos = int(instante.replace(second=0, microsecond=0).timestamp() // 60)
    atualizado_em = iso_utc(instante)
    return [_leitura(ponto, indice, minutos, atualizado_em) for indice, ponto in enumerate(PONTOS)]
