import hashlib
import os
import time
import uuid
from typing import List, Dict, Optional, Tuple, Any
from cryptography.fernet import Fernet
from .models import (
    SecurityEvent,
    CorrelatedIncident,
    Severity,
    Role,
    OperatorVerificationRequest,
    OperatorVerificationResponse,
    LoginRequest,
    LoginResponse,
    RBACCheckRequest,
    RBACCheckResponse,
    CryptoInspectionResponse
)
from .assets import asset_manager


# Role-Based Permission Matrix for Industrial Operations
ROLE_PERMISSIONS: Dict[Role, List[str]] = {
    Role.OPERATOR: [
        "view_telemetry",
        "acknowledge_low_alert",
        "view_asset_status"
    ],
    Role.ENGINEER: [
        "view_telemetry",
        "acknowledge_low_alert",
        "acknowledge_high_alert",
        "view_asset_status",
        "tune_setpoint",
        "inspect_firmware",
        "modify_plc_logic"
    ],
    Role.ADMIN: [
        "view_telemetry",
        "acknowledge_low_alert",
        "acknowledge_high_alert",
        "view_asset_status",
        "tune_setpoint",
        "inspect_firmware",
        "modify_plc_logic",
        "bypass_safety_sis",
        "update_firewall",
        "rotate_crypto_keys",
        "manage_user_roles"
    ]
}

# Simulated registered operators (Badge IDs + Salted SHA-256 PIN Hashes)
# Zero real biometric data is stored or processed.
OPERATOR_DATABASE = {
    "BADGE-OP-401": {
        "name": "Sarah Connor (Turbine Operator)",
        "role": Role.OPERATOR,
        "pin_salt": "salt_alpha_912",
        # SHA-256 of "salt_alpha_912" + "1234"
        "pin_hash": hashlib.sha256("salt_alpha_9121234".encode()).hexdigest()
    },
    "BADGE-ENG-802": {
        "name": "Marcus Vance (Control Systems Engineer)",
        "role": Role.ENGINEER,
        "pin_salt": "salt_beta_456",
        # SHA-256 of "salt_beta_456" + "5678"
        "pin_hash": hashlib.sha256("salt_beta_4565678".encode()).hexdigest()
    },
    "BADGE-ADM-999": {
        "name": "Elena Rostova (Chief OT Cybersecurity Officer)",
        "role": Role.ADMIN,
        "pin_salt": "salt_gamma_789",
        # SHA-256 of "salt_gamma_789" + "9999"
        "pin_hash": hashlib.sha256("salt_gamma_7899999".encode()).hexdigest()
    }
}

# User Account Directory for Authentication Console
USER_DIRECTORY: Dict[str, Dict[str, Any]] = {
    "operator": {
        "user_id": "operator",
        "passwords": ["operator123", "password123", "1234"],
        "name": "Sarah Connor",
        "title": "Turbine Operations Specialist",
        "role": Role.OPERATOR,
        "badge_id": "BADGE-OP-401"
    },
    "engineer": {
        "user_id": "engineer",
        "passwords": ["engineer123", "password123", "5678"],
        "name": "Marcus Vance",
        "title": "Control Systems Lead Engineer",
        "role": Role.ENGINEER,
        "badge_id": "BADGE-ENG-802"
    },
    "admin": {
        "user_id": "admin",
        "passwords": ["admin123", "password123", "9999"],
        "name": "Elena Rostova",
        "title": "Chief OT Cybersecurity Officer",
        "role": Role.ADMIN,
        "badge_id": "BADGE-ADM-999"
    }
}


class SecurityEngine:
    """
    Core industrial cybersecurity engine:
    - User authentication & session generation
    - Simulated events and live stream
    - Correlation engine (OT protocol anomalies + operator security events)
    - Role-Based Access Control (RBAC) with unauthorized access alerts
    - Safe Operator Verification simulation (zero biometric data)
    - Hashing and Fernet symmetric encryption for sensitive demo safety setpoints
    """

    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.correlated_incidents: List[CorrelatedIncident] = []
        
        # Initialize Cryptographic demo keys for sensitive PLC config
        self.fernet_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.fernet_key)
        
        # Secret simulated industrial config
        self.raw_plc_config = (
            "SAFETY_POLICY_REV_4: TURBINE_MAX_RPM=3600; "
            "EMERGENCY_SHUTDOWN_PRESSURE_BAR=185.5; "
            "SIS_KEYSWITCH_MODE=RUN; FAILSAFE_TRIP_DELAY_MS=150"
        )
        self.encrypted_plc_config = self.cipher_suite.encrypt(self.raw_plc_config.encode()).decode()

        self._seed_initial_events()

    def _seed_initial_events(self):
        """Seeds realistic industrial OT security events."""
        event_1 = SecurityEvent(
            id="EVT-1001",
            timestamp="11:32:15",
            source_asset_id="DMZ-FIREWALL",
            target_asset_id="ENG-WORKSTATION-01",
            event_type="UNUSUAL_RDP_TRAFFIC",
            severity=Severity.MEDIUM,
            description="Remote access session initiated outside scheduled maintenance hours.",
            raw_payload_hash=hashlib.sha256(b"RDP_SESSION_SYN_192.168.10.1").hexdigest()[:16],
            correlated=True,
            correlation_id="INC-CORR-01"
        )

        event_2 = SecurityEvent(
            id="EVT-1002",
            timestamp="11:34:40",
            source_asset_id="ENG-WORKSTATION-01",
            target_asset_id="ENG-WORKSTATION-01",
            event_type="OPERATOR_VERIFICATION_FAILED",
            severity=Severity.HIGH,
            description="Simulated operator badge rejected: Invalid cryptographic challenge response 3 consecutive times.",
            raw_payload_hash=hashlib.sha256(b"BADGE_REJECT_CHALLENGE_FAIL").hexdigest()[:16],
            correlated=True,
            correlation_id="INC-CORR-01"
        )

        event_3 = SecurityEvent(
            id="EVT-1003",
            timestamp="11:36:02",
            source_asset_id="ENG-WORKSTATION-01",
            target_asset_id="PLC-TURBINE-01",
            event_type="UNAUTHORIZED_MODBUS_WRITE",
            severity=Severity.CRITICAL,
            description="Modbus Function Code 16 (Write Multiple Registers) targeting turbine speed governor without active work order.",
            raw_payload_hash=hashlib.sha256(b"MODBUS_FC16_REG_40001_WRITE").hexdigest()[:16],
            correlated=True,
            correlation_id="INC-CORR-01"
        )

        self.events.extend([event_1, event_2, event_3])

        # Initial correlated incident linking physical/operator anomaly with Modbus attack
        initial_incident = CorrelatedIncident(
            id="INC-CORR-01",
            title="Correlated Incident: Rogue Workstation Takeover & Unauthorized Modbus Write",
            severity=Severity.CRITICAL,
            timestamp="11:36:10",
            summary=(
                "Correlation engine detected a sequence: Off-hours DMZ ingress (EVT-1001) followed by failed operator "
                "verification attempts (EVT-1002), culminating in an unauthenticated Modbus write (EVT-1003) to Gas Turbine PLC-01."
            ),
            involved_events=["EVT-1001", "EVT-1002", "EVT-1003"],
            involved_assets=["DMZ-FIREWALL", "ENG-WORKSTATION-01", "PLC-TURBINE-01"],
            recommended_action=(
                "Isolate Engineering Workstation EWS-01 from the control subnet immediately. Check physical key-switch "
                "on PLC-TURBINE-01 to ensure RUN mode is active."
            )
        )
        self.correlated_incidents.append(initial_incident)

        # Mark compromised asset
        asset_manager.set_compromised("ENG-WORKSTATION-01", True)

    def get_events(self) -> List[SecurityEvent]:
        return sorted(self.events, key=lambda x: x.id, reverse=True)

    def get_correlated_incidents(self) -> List[CorrelatedIncident]:
        return sorted(self.correlated_incidents, key=lambda x: x.id, reverse=True)

    def authenticate_user(self, req: LoginRequest) -> LoginResponse:
        """
        Authenticates an industrial user by User ID & Password.
        Supports standard usernames ('operator', 'engineer', 'admin') or badge IDs ('BADGE-OP-401').
        Tracks failed login attempts and generates a security alert on unauthorized access.
        """
        uid = req.user_id.strip().lower()
        pwd = req.password.strip()
        current_time = time.strftime("%H:%M:%S")

        matched_user = None

        # Check standard user directory
        if uid in USER_DIRECTORY:
            matched_user = USER_DIRECTORY[uid]
            valid_passwords = matched_user["passwords"]
            is_valid_pwd = pwd in valid_passwords
        else:
            # Check badge IDs
            for badge_id, badge_info in OPERATOR_DATABASE.items():
                if badge_id.lower() == uid:
                    matched_user = {
                        "user_id": badge_id,
                        "name": badge_info["name"],
                        "role": badge_info["role"],
                        "badge_id": badge_id
                    }
                    computed_hash = hashlib.sha256((badge_info["pin_salt"] + pwd).encode()).hexdigest()
                    is_valid_pwd = (computed_hash == badge_info["pin_hash"])
                    break
            else:
                is_valid_pwd = False

        if not matched_user or not is_valid_pwd:
            # Generate security alert for failed login attempt
            alert_evt = SecurityEvent(
                id=f"EVT-{len(self.events) + 1001}",
                timestamp=current_time,
                source_asset_id="DMZ-FIREWALL",
                target_asset_id=None,
                event_type="FAILED_OPERATOR_AUTHENTICATION",
                severity=Severity.HIGH,
                description=f"Failed login attempt for user/badge ID '{req.user_id}' on IndustrialShield console.",
                raw_payload_hash=hashlib.sha256(f"AUTH_FAIL:{req.user_id}:{time.time()}".encode()).hexdigest()[:16]
            )
            self.events.insert(0, alert_evt)
            self._evaluate_correlations()

            return LoginResponse(
                success=False,
                message="Invalid User ID or Password. Authentication denied."
            )

        # Successful authentication
        token = f"TOKEN-SESSION-{uuid.uuid4().hex[:12].upper()}"
        role = matched_user["role"]
        permissions = ROLE_PERMISSIONS.get(role, [])

        return LoginResponse(
            success=True,
            message="Authentication successful.",
            user_id=matched_user["user_id"],
            operator_name=matched_user["name"],
            role=role,
            session_token=token,
            permissions=permissions,
            face_verified_demo=req.face_verified
        )

    def get_demo_users(self) -> List[Dict[str, str]]:
        """Returns safe demo user metadata to guide hackathon judges and operators."""
        return [
            {
                "user_id": "operator",
                "name": "Sarah Connor",
                "role": "operator",
                "default_password": "operator123",
                "description": "Standard plant operator with read-only & low-severity alert acknowledge rights."
            },
            {
                "user_id": "engineer",
                "name": "Marcus Vance",
                "role": "engineer",
                "default_password": "engineer123",
                "description": "Control systems engineer with setpoint tuning & PLC logic modification rights."
            },
            {
                "user_id": "admin",
                "name": "Elena Rostova",
                "role": "admin",
                "default_password": "admin123",
                "description": "Chief cybersecurity administrator with perimeter firewall & safety bypass audit rights."
            }
        ]

    def verify_operator_safe(self, req: OperatorVerificationRequest) -> OperatorVerificationResponse:
        """
        Simulate operator verification using safe cryptographic authentication.
        Strictly zero real biometric data is accepted or collected.
        Verifies badge ID against salted SHA-256 PIN hash.
        """
        record = OPERATOR_DATABASE.get(req.badge_id)
        current_time = time.strftime("%H:%M:%S")

        if not record:
            # Generate security alert for unknown badge
            alert_event = SecurityEvent(
                id=f"EVT-{len(self.events) + 1001}",
                timestamp=current_time,
                source_asset_id=req.workstation_id,
                target_asset_id=None,
                event_type="UNREGISTERED_OPERATOR_BADGE_ATTEMPT",
                severity=Severity.HIGH,
                description=f"Unregistered badge ID '{req.badge_id}' attempted authentication on {req.workstation_id}.",
                raw_payload_hash=hashlib.sha256(f"{req.badge_id}:{time.time()}".encode()).hexdigest()[:16]
            )
            self.events.insert(0, alert_event)
            self._evaluate_correlations()

            return OperatorVerificationResponse(
                success=False,
                message=f"Access Denied: Badge ID '{req.badge_id}' not found in authorization directory.",
                alert_generated=True
            )

        # Check salted SHA-256 PIN
        computed_hash = hashlib.sha256((record["pin_salt"] + req.pin_code).encode()).hexdigest()
        if computed_hash != record["pin_hash"]:
            # Generate security alert for failed PIN
            alert_event = SecurityEvent(
                id=f"EVT-{len(self.events) + 1001}",
                timestamp=current_time,
                source_asset_id=req.workstation_id,
                target_asset_id=None,
                event_type="OPERATOR_PIN_VERIFICATION_FAILED",
                severity=Severity.HIGH,
                description=f"Failed cryptographic challenge for authorized badge '{req.badge_id}' on {req.workstation_id}.",
                raw_payload_hash=hashlib.sha256(f"FAILED_PIN:{req.badge_id}:{time.time()}".encode()).hexdigest()[:16]
            )
            self.events.insert(0, alert_event)
            self._evaluate_correlations()

            return OperatorVerificationResponse(
                success=False,
                message="Access Denied: Cryptographic challenge PIN mismatch.",
                alert_generated=True
            )

        # Successful verification
        session_token = f"TOKEN-SESSION-{uuid.uuid4().hex[:12].upper()}"
        return OperatorVerificationResponse(
            success=True,
            operator_name=record["name"],
            assigned_role=record["role"],
            session_token=session_token,
            message=f"Operator '{record['name']}' verified successfully. Assigned role: {record['role'].value.upper()}.",
            alert_generated=False
        )

    def check_rbac_permission(self, req: RBACCheckRequest) -> RBACCheckResponse:
        """
        Enforces Role-Based Access Control (RBAC).
        If an unauthorized role attempts a restricted industrial command,
        an immediate UNAUTHORIZED_ACCESS_ALERT is logged to the security event stream!
        """
        allowed_actions = ROLE_PERMISSIONS.get(req.role, [])
        is_allowed = req.action in allowed_actions
        current_time = time.strftime("%H:%M:%S")

        if not is_allowed:
            # Generate high severity unauthorized access alert
            alert_event = SecurityEvent(
                id=f"EVT-{len(self.events) + 1001}",
                timestamp=current_time,
                source_asset_id="ENG-WORKSTATION-01",
                target_asset_id=req.target_asset_id,
                event_type="UNAUTHORIZED_ACCESS_ALERT",
                severity=Severity.HIGH if req.role != Role.OPERATOR else Severity.CRITICAL,
                description=(
                    f"RBAC VIOLATION: Role '{req.role.value.upper()}' attempted unauthorized command '{req.action}' "
                    f"on target asset '{req.target_asset_id}'."
                ),
                raw_payload_hash=hashlib.sha256(f"RBAC_BLOCKED:{req.role}:{req.action}:{time.time()}".encode()).hexdigest()[:16]
            )
            self.events.insert(0, alert_event)
            self._evaluate_correlations()

            return RBACCheckResponse(
                allowed=False,
                role=req.role,
                action=req.action,
                target_asset_id=req.target_asset_id,
                alert_generated=True,
                reason=f"Action '{req.action}' requires higher privilege level than '{req.role.value.upper()}'. Security alert logged."
            )

        return RBACCheckResponse(
            allowed=True,
            role=req.role,
            action=req.action,
            target_asset_id=req.target_asset_id,
            alert_generated=False,
            reason=f"Action '{req.action}' is authorized for role '{req.role.value.upper()}'."
        )

    def add_custom_event(self, source_id: str, target_id: Optional[str], event_type: str, severity: Severity, description: str) -> SecurityEvent:
        """Adds a simulated security event and re-evaluates multi-stage correlations."""
        current_time = time.strftime("%H:%M:%S")
        evt = SecurityEvent(
            id=f"EVT-{len(self.events) + 1001}",
            timestamp=current_time,
            source_asset_id=source_id,
            target_asset_id=target_id,
            event_type=event_type,
            severity=severity,
            description=description,
            raw_payload_hash=hashlib.sha256(f"{source_id}:{event_type}:{time.time()}".encode()).hexdigest()[:16]
        )
        self.events.insert(0, evt)
        self._evaluate_correlations()
        return evt

    def _evaluate_correlations(self):
        """
        Correlation Engine:
        Correlates multiple disparate events (e.g. operator verification failure,
        unauthorized access alerts, Modbus manipulation, DMZ anomalies)
        into unified Industrial Incidents.
        """
        recent = self.events[:6]
        event_types = [e.event_type for e in recent]

        # Scenario 1: Lateral Movement & Ladder Logic Modification
        if any("RBAC" in et or "UNAUTHORIZED" in et or "AUTH" in et for et in event_types) and any("MODBUS" in et or "FIRMWARE" in et for et in event_types):
            existing_ids = [inc.id for inc in self.correlated_incidents]
            inc_id = f"INC-CORR-{len(self.correlated_incidents) + 1:02d}"
            
            # Avoid duplicate rapid correlations with exact same events
            inv_evts = [e.id for e in recent[:3]]
            if not any(set(inc.involved_events) == set(inv_evts) for inc in self.correlated_incidents):
                incident = CorrelatedIncident(
                    id=inc_id,
                    title="Correlated Incident: Multi-Vector OT Intrusion & Privilege Escalation",
                    severity=Severity.CRITICAL,
                    timestamp=time.strftime("%H:%M:%S"),
                    summary=(
                        f"Automated correlation engine linked unauthorized RBAC privilege violation with real-time "
                        f"protocol tampering across assets {[e.source_asset_id for e in recent[:3]]}."
                    ),
                    involved_events=inv_evts,
                    involved_assets=list(set([e.source_asset_id for e in recent[:3]] + [e.target_asset_id for e in recent[:3] if e.target_asset_id])),
                    recommended_action="Execute emergency network segmentation. Switch safety controllers to local manual override."
                )
                self.correlated_incidents.insert(0, incident)
                for e in recent[:3]:
                    e.correlated = True
                    e.correlation_id = inc_id

    def get_crypto_inspection(self) -> CryptoInspectionResponse:
        """
        Returns educational demonstration of hashing and symmetric encryption concepts:
        - Plaintext PIN vs Salted SHA-256 Hash
        - Plaintext PLC Safety Config vs AES-128 Fernet Ciphertext
        """
        demo_credentials = []
        for badge, data in OPERATOR_DATABASE.items():
            demo_credentials.append({
                "badge_id": badge,
                "operator_name": data["name"],
                "role": data["role"].value.upper(),
                "salt": data["pin_salt"],
                "stored_hash": data["pin_hash"]
            })

        return CryptoInspectionResponse(
            credentials_demo=demo_credentials,
            encrypted_plc_config={
                "plaintext_preview": self.raw_plc_config,
                "cipher_algorithm": "Fernet (AES-128-CBC + HMAC-SHA256 authenticated)",
                "ciphertext": self.encrypted_plc_config,
                "encryption_key_fingerprint": hashlib.sha256(self.fernet_key).hexdigest()[:20] + "..."
            },
            safety_statement=(
                "Safety & Privacy Guarantee: No real biometric data is collected, stored, or processed. "
                "All verification relies on cryptographic hashing concepts and simulated challenge tokens."
            )
        )


# Singleton instance
security_engine = SecurityEngine()
