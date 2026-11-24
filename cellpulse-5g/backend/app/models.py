from pydantic import BaseModel, Field
from typing import List, Optional


class CellNode(BaseModel):
    id: str
    name: str
    zone: str
    lat: float
    lng: float
    tier: str  # "base" | "pro" | "sim"
    eirp_dbm: float
    rsrp_dbm: float
    sinr_db: float
    radius_m: int
    throughput_mbps: int
    latency_ms: float


class CapexSimulationRequest(BaseModel):
    include_pro: bool = False
    deploy_south_west: bool = True


class CapexSimulationResponse(BaseModel):
    active_nodes: int
    total_throughput_mbps: int
    avg_latency_ms: float
    sla_availability_pct: float
    fleet_risk_usd_hr: float
    estimated_capex_usd: float
    roi_months: float
    simulated_cells: List[CellNode]


class SubscriptionRequest(BaseModel):
    responsible_name: str = Field(..., min_length=3)
    company_name: str = Field(..., min_length=2)
    corporate_email: str
    phone: str
    card_last4: str = Field(..., min_length=4, max_length=4)


class SubscriptionResponse(BaseModel):
    license_id: str
    status: str
    company_name: str
    unlocked_cells: int
    message: str
