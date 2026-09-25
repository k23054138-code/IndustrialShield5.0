from typing import Dict, List, Optional, Tuple
from .models import Asset, AssetStage, AssetStatus, Severity


INITIAL_ASSETS: Dict[str, Asset] = {
    "CORP-ERP": Asset(
        id="CORP-ERP",
        name="Corporate ERP Server",
        stage=AssetStage.LEVEL_4_ENTERPRISE,
        status=AssetStatus.ONLINE,
        ip_address="10.100.1.15",
        protocol="HTTPS / REST",
        criticality=2,
        is_compromised=False,
        risk_score=15.0,
        description="Enterprise Resource Planning system scheduling plant production orders."
    ),
    "DMZ-FIREWALL": Asset(
        id="DMZ-FIREWALL",
        name="Industrial Perimeter Firewall",
        stage=AssetStage.LEVEL_3_5_DMZ,
        status=AssetStatus.ONLINE,
        ip_address="192.168.10.1",
        protocol="Stateful Inspection / IPsec",
        criticality=4,
        is_compromised=False,
        risk_score=25.0,
        description="Dual-homed security boundary separating corporate enterprise and OT operations."
    ),
    "DMZ-HISTORIAN-MIRROR": Asset(
        id="DMZ-HISTORIAN-MIRROR",
        name="DMZ Historian Replica",
        stage=AssetStage.LEVEL_3_5_DMZ,
        status=AssetStatus.ONLINE,
        ip_address="192.168.10.50",
        protocol="OPC UA / TLS",
        criticality=3,
        is_compromised=False,
        risk_score=20.0,
        description="Replicated time-series database providing read-only production analytics to IT."
    ),
    "SCADA-SERVER-01": Asset(
        id="SCADA-SERVER-01",
        name="Central SCADA Supervisory Host",
        stage=AssetStage.LEVEL_3_OPERATIONS,
        status=AssetStatus.ONLINE,
        ip_address="192.168.20.10",
        protocol="Modbus TCP / DNP3",
        criticality=5,
        is_compromised=False,
        risk_score=35.0,
        description="Supervisory control and data acquisition host aggregating plant telemetry."
    ),
    "ENG-WORKSTATION-01": Asset(
        id="ENG-WORKSTATION-01",
        name="Engineering Workstation EWS-01",
        stage=AssetStage.LEVEL_3_OPERATIONS,
        status=AssetStatus.ONLINE,
        ip_address="192.168.20.25",
        protocol="Proprietary Engineering / S7comm",
        criticality=5,
        is_compromised=False,
        risk_score=30.0,
        description="Privileged engineering laptop used for PLC logic programming and firmware downloads."
    ),
    "PLANT-HISTORIAN": Asset(
        id="PLANT-HISTORIAN",
        name="Internal Plant Historian",
        stage=AssetStage.LEVEL_3_OPERATIONS,
        status=AssetStatus.ONLINE,
        ip_address="192.168.20.50",
        protocol="OPC Foundation DA/HDA",
        criticality=3,
        is_compromised=False,
        risk_score=20.0,
        description="Core operational repository recording second-by-second turbine temperature & pressure."
    ),
    "HMI-TURBINE": Asset(
        id="HMI-TURBINE",
        name="Turbine Operator HMI Touchpanel",
        stage=AssetStage.LEVEL_2_CONTROL,
        status=AssetStatus.ONLINE,
        ip_address="192.168.30.12",
        protocol="Modbus TCP",
        criticality=4,
        is_compromised=False,
        risk_score=28.0,
        description="Floor-level touchscreen interface displaying turbine RPM and exhaust heat to operators."
    ),
    "HMI-COOLING": Asset(
        id="HMI-COOLING",
        name="Cooling Subsystem HMI",
        stage=AssetStage.LEVEL_2_CONTROL,
        status=AssetStatus.ONLINE,
        ip_address="192.168.30.14",
        protocol="EtherNet/IP",
        criticality=3,
        is_compromised=False,
        risk_score=18.0,
        description="Operator panel monitoring water chiller flow rate and secondary loop pressure."
    ),
    "PLC-TURBINE-01": Asset(
        id="PLC-TURBINE-01",
        name="Gas Turbine Controller PLC-01",
        stage=AssetStage.LEVEL_1_BASIC_CONTROL,
        status=AssetStatus.ONLINE,
        ip_address="192.168.40.101",
        protocol="Modbus TCP / IEC 61131-3",
        criticality=5,
        is_compromised=False,
        risk_score=40.0,
        description="Real-time controller managing fuel injection valves and turbine rotational speed."
    ),
    "PLC-COOLING-02": Asset(
        id="PLC-COOLING-02",
        name="Cooling Loop Controller PLC-02",
        stage=AssetStage.LEVEL_1_BASIC_CONTROL,
        status=AssetStatus.ONLINE,
        ip_address="192.168.40.102",
        protocol="Modbus TCP",
        criticality=4,
        is_compromised=False,
        risk_score=22.0,
        description="Controls secondary refrigerant compressors and coolant circulation."
    ),
    "SIS-01": Asset(
        id="SIS-01",
        name="Emergency Safety Instrumented System (SIS)",
        stage=AssetStage.LEVEL_1_BASIC_CONTROL,
        status=AssetStatus.ONLINE,
        ip_address="192.168.40.200",
        protocol="Safety-Ethernet / SIL-3",
        criticality=5,
        is_compromised=False,
        risk_score=10.0,
        description="Safety Integrity Level 3 autonomous system that executes emergency shutdown (ESD) if thresholds breach."
    ),
    "VALVE-PRESSURE-01": Asset(
        id="VALVE-PRESSURE-01",
        name="Turbine Overpressure Relief Actuator",
        stage=AssetStage.LEVEL_0_FIELD,
        status=AssetStatus.ONLINE,
        ip_address="Hardwired 4-20mA / Fieldbus",
        protocol="HART / Analog Loop",
        criticality=5,
        is_compromised=False,
        risk_score=15.0,
        description="Physical pneumatic dump valve that releases steam during overpressure events."
    ),
    "TEMP-SENSOR-01": Asset(
        id="TEMP-SENSOR-01",
        name="Turbine Core Thermocouple Cluster",
        stage=AssetStage.LEVEL_0_FIELD,
        status=AssetStatus.ONLINE,
        ip_address="Hardwired RTD Loop",
        protocol="Modbus RTU over RS-485",
        criticality=4,
        is_compromised=False,
        risk_score=12.0,
        description="Thermal sensors monitoring combustion chamber temperature in real time."
    ),
    "PUMP-COOLING-01": Asset(
        id="PUMP-COOLING-01",
        name="Auxiliary Coolant Injection Pump",
        stage=AssetStage.LEVEL_0_FIELD,
        status=AssetStatus.ONLINE,
        ip_address="Hardwired Relay",
        protocol="Discrete 24V I/O",
        criticality=3,
        is_compromised=False,
        risk_score=10.0,
        description="Centrifugal pump maintaining high-pressure circulation of cooling fluid."
    )
}


class AssetManager:
    """Manages industrial asset state, Purdue stage hierarchy, online/offline availability, and risk calculations."""

    def __init__(self):
        # Deep copy initial assets
        self.assets: Dict[str, Asset] = {k: v.model_copy() for k, v in INITIAL_ASSETS.items()}

    def get_all_assets(self) -> List[Asset]:
        return list(self.assets.values())

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        return self.assets.get(asset_id)

    def toggle_status(self, asset_id: str) -> Optional[Asset]:
        asset = self.assets.get(asset_id)
        if not asset:
            return None
        
        if asset.status == AssetStatus.ONLINE:
            asset.status = AssetStatus.OFFLINE
        elif asset.status == AssetStatus.OFFLINE:
            asset.status = AssetStatus.ONLINE
        elif asset.status == AssetStatus.DEGRADED:
            asset.status = AssetStatus.ONLINE
        return asset

    def set_compromised(self, asset_id: str, compromised: bool = True) -> Optional[Asset]:
        asset = self.assets.get(asset_id)
        if not asset:
            return None
        asset.is_compromised = compromised
        if compromised:
            asset.risk_score = min(100.0, asset.risk_score + 45.0)
        else:
            asset.risk_score = max(10.0, asset.risk_score - 45.0)
        return asset

    def reset_all(self):
        self.assets = {k: v.model_copy() for k, v in INITIAL_ASSETS.items()}

    def calculate_circular_risk(self, active_threats_count: int = 0) -> Tuple[float, str, str, str]:
        """
        Calculates the plant-wide cyber-physical risk score (0-100),
        the human-readable risk level, the exact color code for the circular gauge,
        and an analytical summary.
        """
        total = len(self.assets)
        if total == 0:
            return 0.0, "Low", "#10b981", "No industrial assets registered."

        compromised_count = sum(1 for a in self.assets.values() if a.is_compromised)
        offline_count = sum(1 for a in self.assets.values() if a.status == AssetStatus.OFFLINE)
        
        # Weighted risk calculation:
        # 1. Base average risk score of online/compromised assets
        weighted_scores = []
        for a in self.assets.values():
            multiplier = 1.0
            if a.is_compromised:
                multiplier = 1.8
            # Criticality weighting (1-5)
            weight = a.criticality * 0.4
            # If asset is offline, it can impact plant availability or represent an isolated safety measure
            base_score = a.risk_score if a.status != AssetStatus.OFFLINE else 5.0
            weighted_scores.append(base_score * weight * multiplier)

        raw_score = sum(weighted_scores) / (sum(a.criticality * 0.4 for a in self.assets.values()) or 1.0)
        
        # Threat amplification
        threat_penalty = active_threats_count * 8.5
        compromised_penalty = compromised_count * 16.0
        
        score = min(100.0, max(5.0, raw_score + threat_penalty + compromised_penalty))
        score = round(score, 1)

        # Dynamic Color Scheme for the Circular Detection Gauge:
        # Green -> Yellow -> Orange -> Crimson Red
        if score <= 25.0:
            level = "Low"
            color = "#10b981"  # Emerald Green (Safe Operational Baseline)
            summary = "Plant perimeter and control loops are stable. No active adversarial traversal detected."
        elif score <= 55.0:
            level = "Medium"
            color = "#f59e0b"  # Amber/Yellow (Elevated Vigilance)
            summary = "Suspicious traffic or offline redundancy detected. Engineering supervision recommended."
        elif score <= 80.0:
            level = "High"
            color = "#f97316"  # Orange (High Cyber Threat)
            summary = "Significant lateral movement or unauthorized command path observed near Level 1/2 controllers."
        else:
            level = "Critical"
            color = "#ef4444"  # Crimson Red (Critical Emergency)
            summary = "Active exposure path reaching Safety Instrumented System (SIS) or Core Turbine PLC. Immediate isolation required!"

        return score, level, color, summary

    def get_stage_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Groups assets by Purdue Model Stage and returns status and risk analysis."""
        breakdown: Dict[str, Dict[str, Any]] = {}
        for stage in AssetStage:
            assets_in_stage = [a for a in self.assets.values() if a.stage == stage]
            online_count = sum(1 for a in assets_in_stage if a.status == AssetStatus.ONLINE)
            compromised_count = sum(1 for a in assets_in_stage if a.is_compromised)
            avg_risk = sum(a.risk_score for a in assets_in_stage) / len(assets_in_stage) if assets_in_stage else 0.0

            breakdown[stage.value] = {
                "total": len(assets_in_stage),
                "online": online_count,
                "offline": len(assets_in_stage) - online_count,
                "compromised": compromised_count,
                "avg_risk": round(avg_risk, 1),
                "assets": [a.id for a in assets_in_stage]
            }
        return breakdown


# Singleton instance for the application
asset_manager = AssetManager()
