from fastapi.testclient import TestClient
from app.main import app, calculate_fspl_rsrp

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_base_vs_pro_cells_count():
    base_res = client.get("/api/v1/cells?include_pro=false")
    pro_res = client.get("/api/v1/cells?include_pro=true")
    assert len(base_res.json()) == 5
    assert len(pro_res.json()) == 20


def test_capex_simulation_mitigates_fleet_risk():
    res = client.post("/api/v1/simulate-capex", json={"include_pro": False, "deploy_south_west": True})
    data = res.json()
    assert res.status_code == 200
    assert data["active_nodes"] == 7
    assert data["fleet_risk_usd_hr"] == 0.0
    assert data["sla_availability_pct"] >= 98.5


def test_fspl_propagation_physics():
    near_rsrp = calculate_fspl_rsrp(eirp_dbm=64.0, distance_km=0.5)
    far_rsrp = calculate_fspl_rsrp(eirp_dbm=64.0, distance_km=3.0)
    assert near_rsrp > far_rsrp
