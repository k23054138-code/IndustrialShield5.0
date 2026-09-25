from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AssetStage(str, Enum):
    LEVEL_4_ENTERPRISE = "Level 4: Enterprise Network"
    LEVEL_3_5_DMZ = "Level 3.5: Industrial DMZ"
    LEVEL_3_OPERATIONS = "Level 3: Operations & SCADA"
    LEVEL_2_CONTROL = "Level 2: Supervisory Control"
    LEVEL_1_BASIC_CONTROL = "Level 1: Basic Control & Safety"
    LEVEL_0_FIELD = "Level 0: Physical Field Devices"


class AssetStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"
    MAINTENANCE = "MAINTENANCE"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Role(str, Enum):
    OPERATOR = "operator"
    ENGINEER = "engineer"
    ADMIN = "admin"


class Asset(BaseModel):
    id: str
    name: str
    stage: AssetStage
    status: AssetStatus
    ip_address: str
    protocol: str
    criticality: int = Field(ge=1, le=5, description="1 is low, 5 is critical safety asset")
    is_compromised: bool = False
    risk_score: float = Field(ge=0.0, le=100.0, default=0.0)
    description: str


class SecurityEvent(BaseModel):
    id: str
    timestamp: str
    source_asset_id: str
    target_asset_id: Optional[str] = None
    event_type: str
    severity: Severity
    description: str
    raw_payload_hash: str
    correlated: bool = False
    correlation_id: Optional[str] = None


class CorrelatedIncident(BaseModel):
    id: str
    title: str
    severity: Severity
    timestamp: str
    summary: str
    involved_events: List[str]
    involved_assets: List[str]
    recommended_action: str


class ImpactAnalysisRequest(BaseModel):
    source_node: str
    target_node: Optional[str] = None


class ImpactAnalysisResponse(BaseModel):
    source_node: str
    target_node: Optional[str] = None
    exposure_paths: List[List[str]]
    blast_radius_nodes: List[str]
    critical_assets_at_risk: List[str]
    exposure_risk_score: float
    blast_radius_count: int
    mitigation_steps: List[str]


class OperatorVerificationRequest(BaseModel):
    badge_id: str
    pin_code: str
    workstation_id: str


class OperatorVerificationResponse(BaseModel):
    success: bool
    operator_name: Optional[str] = None
    assigned_role: Optional[Role] = None
    verification_method: str = "Safe Cryptographic Token (Zero Biometric Data Used)"
    session_token: Optional[str] = None
    message: str
    alert_generated: bool = False


class LoginRequest(BaseModel):
    user_id: str
    password: str
    face_verified: bool = False


class LoginResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    operator_name: Optional[str] = None
    role: Optional[Role] = None
    session_token: Optional[str] = None
    permissions: List[str] = []
    face_verified_demo: bool = False


class RBACCheckRequest(BaseModel):
    role: Role
    action: str
    target_asset_id: str
    operator_name: Optional[str] = "Demo User"


class RBACCheckResponse(BaseModel):
    allowed: bool
    role: Role
    action: str
    target_asset_id: str
    alert_generated: bool
    reason: str


class ExplainEventRequest(BaseModel):
    event_id: Optional[str] = None
    incident_id: Optional[str] = None
    custom_description: Optional[str] = None


class ExplainEventResponse(BaseModel):
    title: str
    what_happened: str
    cyber_physical_risk: str
    recommended_action: str
    technical_details: Dict[str, Any]
    explainer_mode: str  # "AI (Gemini)" or "Fallback Intelligent Rule-Based Engine"
    # Extended transparent questions for non-technical operators
    why_dangerous: Optional[str] = None
    affected_asset: Optional[str] = None
    propagation_path: Optional[str] = None
    operational_impact: Optional[str] = None
    investigation_steps: Optional[str] = None


class OverallRiskResponse(BaseModel):
    overall_score: float  # 0 to 100
    risk_level: str  # Low, Medium, High, Critical
    color: str  # Hex code for circular detection gauge
    online_count: int
    offline_count: int
    total_assets: int
    compromised_count: int
    stage_breakdown: Dict[str, Dict[str, Any]]
    active_threat_count: int
    analysis_summary: str


class CryptoInspectionResponse(BaseModel):
    credentials_demo: List[Dict[str, str]]
    encrypted_plc_config: Dict[str, str]
    safety_statement: str
