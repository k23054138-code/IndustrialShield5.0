import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .models import (
    Asset,
    SecurityEvent,
    CorrelatedIncident,
    ImpactAnalysisRequest,
    ImpactAnalysisResponse,
    OperatorVerificationRequest,
    OperatorVerificationResponse,
    LoginRequest,
    LoginResponse,
    RBACCheckRequest,
    RBACCheckResponse,
    ExplainEventRequest,
    ExplainEventResponse,
    OverallRiskResponse,
    CryptoInspectionResponse,
    Severity,
    AssetStatus
)
from .assets import asset_manager
from .graph_engine import graph_engine
from .security_engine import security_engine
from .ai_explainer import ai_explainer

# Create FastAPI app
app = FastAPI(
    title="IndustrialShield OT Cybersecurity API",
    description="Cyber-Physical Security Monitoring, NetworkX Impact Analysis, RBAC & AI Explanation for Industrial Control Systems",
    version="1.1.0"
)

# Enable CORS for local testing and hackathon presentation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# ---------------- AUTHENTICATION ENDPOINTS ----------------

@app.post("/api/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Authenticates user/operator credentials.
    Supports standard user IDs ('operator', 'engineer', 'admin') or badge IDs.
    Returns session token, operator name, and role permissions.
    """
    return security_engine.authenticate_user(req)


@app.get("/api/auth/users")
def get_demo_users():
    """Returns safe demo user metadata to guide hackathon evaluation."""
    return security_engine.get_demo_users()


# ---------------- API ENDPOINTS ----------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": "IndustrialShield Cyber-Physical Defense Framework",
        "mode": "Simulation (Safe Hackathon Environment)",
        "networkx_graph_nodes": graph_engine.graph.number_of_nodes(),
        "networkx_graph_edges": graph_engine.graph.number_of_edges()
    }


@app.get("/api/assets", response_model=List[Asset])
def get_assets():
    """Retrieve all industrial assets with Purdue stage, online/offline availability, and risk scores."""
    return asset_manager.get_all_assets()


@app.post("/api/assets/{asset_id}/toggle-status", response_model=Asset)
def toggle_asset_status(asset_id: str):
    """
    Toggle asset availability (ONLINE <-> OFFLINE).
    Demonstrates asset availability tracking and emergency network isolation.
    """
    asset = asset_manager.toggle_status(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    
    current_status = asset.status.value
    severity = Severity.HIGH if current_status == "OFFLINE" and asset.criticality >= 4 else Severity.INFO
    security_engine.add_custom_event(
        source_id=asset_id,
        target_id=None,
        event_type=f"ASSET_STATUS_CHANGED_{current_status}",
        severity=severity,
        description=f"Asset '{asset.name}' is now marked as {current_status}. Availability status updated."
    )
    return asset


@app.post("/api/assets/{asset_id}/toggle-compromised", response_model=Asset)
def toggle_asset_compromised(asset_id: str):
    """Toggle compromised state of an asset for penetration and exposure path simulation."""
    asset = asset_manager.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    
    new_state = not asset.is_compromised
    updated = asset_manager.set_compromised(asset_id, new_state)

    if new_state:
        security_engine.add_custom_event(
            source_id=asset_id,
            target_id=None,
            event_type="ASSET_COMPROMISE_FLAGGED",
            severity=Severity.HIGH,
            description=f"Asset '{asset.name}' flagged as compromised! Blast radius calculation updated."
        )
    return updated


@app.get("/api/risk/overall", response_model=OverallRiskResponse)
def get_overall_risk():
    """
    Calculates overall plant cyber risk score (0-100),
    exact color for the circular detection gauge,
    and stage-by-stage risk breakdown.
    """
    active_threats = len([e for e in security_engine.get_events() if e.severity in (Severity.HIGH, Severity.CRITICAL)])
    score, level, color, summary = asset_manager.calculate_circular_risk(active_threats_count=active_threats)
    
    all_assets = asset_manager.get_all_assets()
    online_count = sum(1 for a in all_assets if a.status == AssetStatus.ONLINE)
    offline_count = sum(1 for a in all_assets if a.status == AssetStatus.OFFLINE)
    compromised_count = sum(1 for a in all_assets if a.is_compromised)

    return OverallRiskResponse(
        overall_score=score,
        risk_level=level,
        color=color,
        online_count=online_count,
        offline_count=offline_count,
        total_assets=len(all_assets),
        compromised_count=compromised_count,
        stage_breakdown=asset_manager.get_stage_breakdown(),
        active_threat_count=active_threats,
        analysis_summary=summary
    )


@app.get("/api/graph")
def get_graph():
    """Returns NetworkX industrial topology with Purdue stages, edges, and chokepoints."""
    return graph_engine.get_topology_data()


@app.post("/api/impact-analysis", response_model=ImpactAnalysisResponse)
def run_impact_analysis(req: ImpactAnalysisRequest):
    """
    Executes NetworkX graph-based exposure path analysis from the source asset.
    Finds shortest paths to critical industrial controllers (PLCs, SIS) and computes blast radius.
    """
    return graph_engine.analyze_impact(req.source_node, req.target_node)


@app.get("/api/events", response_model=List[SecurityEvent])
def get_security_events():
    """Returns the live stream of simulated industrial security events."""
    return security_engine.get_events()


@app.post("/api/simulate-event", response_model=SecurityEvent)
def simulate_event(scenario: str):
    """
    Simulates realistic OT cyber scenarios:
    - 'modbus_flood': Modbus injection to Turbine PLC
    - 'sis_tamper': Safety Instrumented System logic bypass attempt
    - 'firmware_mismatch': Unauthorized firmware hash alteration on PLC
    - 'lateral_pivot': Attacker jumping from DMZ mirror to SCADA host
    """
    if scenario == "modbus_flood":
        return security_engine.add_custom_event(
            source_id="ENG-WORKSTATION-01",
            target_id="PLC-TURBINE-01",
            event_type="UNAUTHORIZED_MODBUS_WRITE",
            severity=Severity.CRITICAL,
            description="High-frequency Modbus write attempt to Turbine Fuel Governor registers (FC 16)."
        )
    elif scenario == "sis_tamper":
        return security_engine.add_custom_event(
            source_id="ENG-WORKSTATION-01",
            target_id="SIS-01",
            event_type="SIS_BYPASS_ATTEMPT",
            severity=Severity.CRITICAL,
            description="Simulated attempt to remotely modify Safety Instrumented System trip thresholds."
        )
    elif scenario == "firmware_mismatch":
        return security_engine.add_custom_event(
            source_id="PLC-COOLING-02",
            target_id=None,
            event_type="FIRMWARE_INTEGRITY_MISMATCH",
            severity=Severity.HIGH,
            description="PLC boot hash does not match engineering baseline signature stored in secure vault."
        )
    elif scenario == "lateral_pivot":
        return security_engine.add_custom_event(
            source_id="DMZ-HISTORIAN-MIRROR",
            target_id="SCADA-SERVER-01",
            event_type="LATERAL_TRAVERSAL_DMZ_TO_OPERATIONS",
            severity=Severity.HIGH,
            description="Anomalous cross-zone connection detected traversing DMZ firewall boundary."
        )
    else:
        return security_engine.add_custom_event(
            source_id="HMI-TURBINE",
            target_id="PLC-TURBINE-01",
            event_type="ABNORMAL_SETPOINT_INPUT",
            severity=Severity.MEDIUM,
            description="Operator panel entered setpoint 15% higher than nominal production envelope."
        )


@app.get("/api/correlations", response_model=List[CorrelatedIncident])
def get_correlations():
    """Returns multi-stage correlated incidents identified by the correlation engine."""
    return security_engine.get_correlated_incidents()


@app.post("/api/operator-verify", response_model=OperatorVerificationResponse)
def verify_operator(req: OperatorVerificationRequest):
    """
    Safe operator verification simulation.
    Uses cryptographic salted SHA-256 PIN matching. Zero real biometric data used.
    """
    return security_engine.verify_operator_safe(req)


@app.post("/api/rbac/check-action", response_model=RBACCheckResponse)
def check_rbac(req: RBACCheckRequest):
    """
    Validates role-based access permissions (Operator vs Engineer vs Admin).
    If an unauthorized action is attempted, automatically generates an UNAUTHORIZED_ACCESS_ALERT!
    """
    return security_engine.check_rbac_permission(req)


@app.post("/api/ai/explain", response_model=ExplainEventResponse)
def explain_security_event(req: ExplainEventRequest):
    """
    Explains industrial security events in simple, non-technical language.
    Uses Gemini API if configured, with guaranteed instant deterministic fallback.
    """
    return ai_explainer.explain(
        event_id=req.event_id,
        incident_id=req.incident_id,
        custom_text=req.custom_description
    )


@app.get("/api/crypto/inspect", response_model=CryptoInspectionResponse)
def inspect_cryptography():
    """Demonstrates cryptographic protection concepts (SHA-256 salted hashes and Fernet AES-128 encryption)."""
    return security_engine.get_crypto_inspection()


@app.post("/api/reset")
def reset_simulation():
    """Resets assets, graph, events, and correlations to clean baseline."""
    asset_manager.reset_all()
    graph_engine._build_topology()
    global security_engine
    security_engine = security_engine.__class__()
    return {"message": "IndustrialShield simulation state reset to nominal baseline."}


# ---------------- FRONTEND STATIC SERVING ----------------

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_frontend_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend index.html not yet built."}
