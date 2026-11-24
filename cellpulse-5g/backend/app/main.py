import asyncio
import json
import math
import os
import random
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    CapexSimulationRequest,
    CapexSimulationResponse,
    CellNode,
    SubscriptionRequest,
    SubscriptionResponse,
)

app = FastAPI(
    title="CellPulse 5G Enterprise NOC API",
    description="Microservicio de telemetría geoespacial 5G NR (3.5 GHz n78), cálculo EIRP/RSRP y analítica B2B SLA.",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a Redis con fallback automático en memoria
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False

MEMORY_CACHE = {}

# Catálogo Maestro de 20 Macro-Celdas (Bogotá D.C. & Sabana)
INITIAL_CELLS: List[CellNode] = [
    CellNode(id="CP-01", name="Centro Internacional", zone="Santa Fe / Centro", lat=4.6155, lng=-74.0695, tier="base", eirp_dbm=62.0, rsrp_dbm=-82.0, sinr_db=19.4, radius_m=3200, throughput_mbps=168, latency_ms=13.4),
    CellNode(id="CP-02", name="Chapinero Alto", zone="Chapinero", lat=4.6485, lng=-74.0620, tier="base", eirp_dbm=62.0, rsrp_dbm=-84.0, sinr_db=18.8, radius_m=3000, throughput_mbps=154, latency_ms=14.1),
    CellNode(id="CP-03", name="Ciudad Salitre", zone="Teusaquillo / Salitre", lat=4.6540, lng=-74.1050, tier="base", eirp_dbm=63.0, rsrp_dbm=-81.0, sinr_db=20.1, radius_m=3300, throughput_mbps=162, latency_ms=13.8),
    CellNode(id="CP-04", name="Portal Calle 80", zone="Engativá", lat=4.7095, lng=-74.1110, tier="base", eirp_dbm=62.0, rsrp_dbm=-85.0, sinr_db=17.9, radius_m=3100, throughput_mbps=138, latency_ms=15.0),
    CellNode(id="CP-05", name="Zona Industrial Puente Aranda", zone="Puente Aranda", lat=4.6260, lng=-74.1130, tier="base", eirp_dbm=61.0, rsrp_dbm=-86.0, sinr_db=17.2, radius_m=2900, throughput_mbps=120, latency_ms=14.7),
    CellNode(id="CP-06", name="Usaquén Santa Bárbara", zone="Usaquén", lat=4.6960, lng=-74.0330, tier="pro", eirp_dbm=64.0, rsrp_dbm=-79.0, sinr_db=22.3, radius_m=3400, throughput_mbps=195, latency_ms=11.8),
    CellNode(id="CP-07", name="Toberín Autopista Norte", zone="Usaquén Norte", lat=4.7460, lng=-74.0450, tier="pro", eirp_dbm=64.0, rsrp_dbm=-80.0, sinr_db=21.8, radius_m=3500, throughput_mbps=188, latency_ms=12.1),
    CellNode(id="CP-08", name="Suba Centro & Niza", zone="Suba", lat=4.7410, lng=-74.0840, tier="pro", eirp_dbm=63.0, rsrp_dbm=-82.0, sinr_db=20.5, radius_m=3300, throughput_mbps=182, latency_ms=12.4),
    CellNode(id="CP-09", name="Suba Tibabuyes", zone="Suba Occidente", lat=4.7480, lng=-74.1160, tier="pro", eirp_dbm=63.0, rsrp_dbm=-83.0, sinr_db=19.8, radius_m=3200, throughput_mbps=171, latency_ms=12.9),
    CellNode(id="CP-10", name="Nodo Sabana Chía", zone="Chía (Sabana Norte)", lat=4.8615, lng=-74.0585, tier="pro", eirp_dbm=65.0, rsrp_dbm=-77.0, sinr_db=24.1, radius_m=3800, throughput_mbps=210, latency_ms=11.5),
    CellNode(id="CP-11", name="Aeropuerto El Dorado", zone="Fontibón", lat=4.6980, lng=-74.1420, tier="pro", eirp_dbm=65.0, rsrp_dbm=-76.0, sinr_db=25.0, radius_m=3600, throughput_mbps=230, latency_ms=10.9),
    CellNode(id="CP-12", name="Parque Industrial Siberia", zone="Cota / Calle 80", lat=4.7420, lng=-74.1780, tier="pro", eirp_dbm=64.0, rsrp_dbm=-78.0, sinr_db=23.2, radius_m=3700, throughput_mbps=204, latency_ms=11.7),
    CellNode(id="CP-13", name="Hub Logístico Funza", zone="Funza (Sabana Occ.)", lat=4.7160, lng=-74.2120, tier="pro", eirp_dbm=64.0, rsrp_dbm=-80.0, sinr_db=21.5, radius_m=3600, throughput_mbps=192, latency_ms=12.2),
    CellNode(id="CP-14", name="Zona Franca Mosquera", zone="Mosquera (Sabana Occ.)", lat=4.7050, lng=-74.2310, tier="pro", eirp_dbm=64.0, rsrp_dbm=-81.0, sinr_db=21.1, radius_m=3500, throughput_mbps=189, latency_ms=12.3),
    CellNode(id="CP-15", name="Corabastos & Américas", zone="Kennedy", lat=4.6290, lng=-74.1550, tier="pro", eirp_dbm=64.0, rsrp_dbm=-79.0, sinr_db=22.6, radius_m=3400, throughput_mbps=205, latency_ms=11.9),
    CellNode(id="CP-16", name="Bosa Centro & El Recreo", zone="Bosa", lat=4.6120, lng=-74.1880, tier="pro", eirp_dbm=63.0, rsrp_dbm=-82.0, sinr_db=20.2, radius_m=3300, throughput_mbps=176, latency_ms=12.6),
    CellNode(id="CP-17", name="Soacha Autopista Sur", zone="Soacha", lat=4.5810, lng=-74.2170, tier="pro", eirp_dbm=65.0, rsrp_dbm=-78.0, sinr_db=23.5, radius_m=3700, throughput_mbps=215, latency_ms=11.4),
    CellNode(id="CP-18", name="San Cristóbal & 20 de Julio", zone="San Cristóbal", lat=4.5730, lng=-74.0880, tier="pro", eirp_dbm=63.0, rsrp_dbm=-83.0, sinr_db=19.5, radius_m=3100, throughput_mbps=164, latency_ms=13.0),
    CellNode(id="CP-19", name="Usme Santa Librada", zone="Usme", lat=4.5180, lng=-74.1150, tier="pro", eirp_dbm=63.0, rsrp_dbm=-84.0, sinr_db=19.1, radius_m=3300, throughput_mbps=158, latency_ms=13.2),
    CellNode(id="CP-20", name="Ciudad Bolívar Mirador", zone="Ciudad Bolívar", lat=4.5650, lng=-74.1560, tier="pro", eirp_dbm=64.0, rsrp_dbm=-80.0, sinr_db=21.4, radius_m=3400, throughput_mbps=179, latency_ms=12.5),
]

CAPEX_NODES: List[CellNode] = [
    CellNode(id="SIM-01", name="CAPEX Ciudad Bolívar Alta", zone="Ciudad Bolívar (Sim)", lat=4.5580, lng=-74.1520, tier="sim", eirp_dbm=64.0, rsrp_dbm=-79.0, sinr_db=22.1, radius_m=3500, throughput_mbps=185, latency_ms=12.0),
    CellNode(id="SIM-02", name="CAPEX Autopista Sur / Bosa", zone="Soacha - Bosa (Sim)", lat=4.5930, lng=-74.1980, tier="sim", eirp_dbm=65.0, rsrp_dbm=-77.0, sinr_db=23.8, radius_m=3600, throughput_mbps=198, latency_ms=11.6),
]


def calculate_fspl_rsrp(eirp_dbm: float, distance_km: float, freq_mhz: float = 3500.0) -> float:
    """Calcula la potencia recibida estimada usando Free Space Path Loss (3GPP n78)."""
    if distance_km <= 0:
        distance_km = 0.05
    fspl = 20 * math.log10(distance_km) + 20 * math.log10(freq_mhz) + 32.44
    # Compensación por ganancia de antena receptora y margen urbano
    return round(eirp_dbm - fspl + 28.5, 2)


@app.get("/health", tags=["Observabilidad"])
def health_check():
    return {
        "status": "healthy",
        "service": "cellpulse-5g-api",
        "redis_cache": "connected" if REDIS_AVAILABLE else "fallback-memory",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/cells", response_model=List[CellNode], tags=["Topología 5G"])
def get_cells(include_pro: bool = False, sector: Optional[str] = None):
    cache_key = f"cells:{include_pro}:{sector or 'all'}"

    if REDIS_AVAILABLE:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    elif cache_key in MEMORY_CACHE:
        return MEMORY_CACHE[cache_key]

    result = [
        c for c in INITIAL_CELLS
        if (c.tier == "base" or (include_pro and c.tier == "pro"))
        and (not sector or sector.lower() in c.zone.lower() or sector.lower() in c.name.lower())
    ]

    serialized = [c.model_dump() for c in result]
    if REDIS_AVAILABLE:
        redis_client.setex(cache_key, 30, json.dumps(serialized))
    else:
        MEMORY_CACHE[cache_key] = serialized

    return serialized


@app.post("/api/v1/simulate-capex", response_model=CapexSimulationResponse, tags=["Analítica CAPEX"])
def simulate_capex(payload: CapexSimulationRequest):
    active = [c for c in INITIAL_CELLS if c.tier == "base" or (payload.include_pro and c.tier == "pro")]
    sim_added = CAPEX_NODES if payload.deploy_south_west else []
    full_topology = active + sim_added

    total_tp = sum(c.throughput_mbps for c in full_topology)
    avg_lat = round(sum(c.latency_ms for c in full_topology) / len(full_topology), 2)
    is_covered = payload.include_pro or payload.deploy_south_west

    sla = 99.8 if payload.include_pro else (98.9 if payload.deploy_south_west else 91.8)
    risk = 0.0 if is_covered else 2150.0
    capex = 48000.0 if payload.deploy_south_west else 0.0
    roi = 2.4 if payload.deploy_south_west else 0.0

    return CapexSimulationResponse(
        active_nodes=len(full_topology),
        total_throughput_mbps=total_tp,
        avg_latency_ms=avg_lat,
        sla_availability_pct=sla,
        fleet_risk_usd_hr=risk,
        estimated_capex_usd=capex,
        roi_months=roi,
        simulated_cells=sim_added,
    )


@app.post("/api/v1/subscriptions", response_model=SubscriptionResponse, tags=["Facturación B2B"])
def create_pro_subscription(sub: SubscriptionRequest):
    license_code = f"CP5G-PRO-{uuid.uuid4().hex[:8].upper()}"
    return SubscriptionResponse(
        license_id=license_code,
        status="ACTIVE",
        company_name=sub.company_name,
        unlocked_cells=20,
        message=f"Licencia Enterprise activada para {sub.company_name}. Nodos metropolitanos habilitados.",
    )


@app.websocket("/ws/telemetry")
async def telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "latency_ms": round(11.8 + random.uniform(-0.4, 0.4), 2),
                "jitter_ms": round(random.uniform(0.3, 1.1), 2),
                "packet_loss_pct": 0.01,
                "active_band": "3.5 GHz (n78)",
            }
            await websocket.send_json(payload)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        pass
