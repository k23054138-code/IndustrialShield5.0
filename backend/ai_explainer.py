import os
import json
from typing import Dict, Any, Optional
from .models import ExplainEventResponse, SecurityEvent, CorrelatedIncident
from .security_engine import security_engine
from .assets import asset_manager


# Curated Plain-Language Knowledge Base for Industrial Cybersecurity Events
FALLBACK_KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    "UNAUTHORIZED_MODBUS_WRITE": {
        "title": "Unauthorized Industrial Protocol Command Attempt",
        "what_happened": (
            "A computer or unauthorized device on the network sent a direct 'write' instruction to an industrial "
            "controller (PLC) without an authorized production work order. In industrial automation, Modbus is the language "
            "used to tell valves how much to open and motors how fast to spin."
        ),
        "why_dangerous": (
            "Industrial controllers directly govern physical mechanical actuators. If an attacker modifies memory registers "
            "without validation, the controller blindly executes commands that can exceed physical engineering tolerances."
        ),
        "propagation_path": (
            "Engineering Workstation (EWS-01) ➔ Level 1 Control Subnet (Modbus Port 502) ➔ Gas Turbine PLC-01 ➔ Overpressure Actuator Valve."
        ),
        "operational_impact": (
            "Combustion chamber overheating, severe fuel air imbalance, emergency turbine trip, or physical steam overpressurization."
        ),
        "investigation_steps": (
            "1. Inspect the physical turbine controller key switch and set it to 'RUN' (disable remote program mode).\n"
            "2. Block communication between the workstation and PLC at the managed industrial switch.\n"
            "3. Verify current turbine speed and exhaust temperature against physical analog gauges."
        ),
        "cyber_physical_risk": (
            "If an unauthorized command changes the controller's settings, physical machinery could overheat, overpressurize, "
            "or damage expensive equipment like gas turbines and high-voltage pumps."
        ),
        "recommended_action": (
            "1. Inspect the physical turbine controller key switch and set it to 'RUN' (disable remote program mode).\n"
            "2. Block communication between the workstation and PLC at the managed industrial switch.\n"
            "3. Verify current turbine speed and exhaust temperature against physical analog gauges."
        )
    },
    "OPERATOR_VERIFICATION_FAILED": {
        "title": "Failed Operator Identity Verification",
        "what_happened": (
            "A person or script at an engineering workstation attempted to log in using an unverified digital security badge "
            "or supplied the wrong security PIN 3 times in a row. The system blocked the session using cryptographic verification."
        ),
        "why_dangerous": (
            "The engineering workstation possesses privileged compilers and ladder logic editors. An unauthorized user sitting at "
            "this console can reprogram controllers and bypass safety shutdown interlocks."
        ),
        "propagation_path": (
            "Console Physical Access ➔ Engineering Software Privileges ➔ Level 3 SCADA Host ➔ Level 1 PLCs."
        ),
        "operational_impact": (
            "Loss of supervisory visibility, potential sabotage of control logic, and rogue downloads of modified firmware."
        ),
        "investigation_steps": (
            "1. Dispatch physical plant security to inspect the Control Room console.\n"
            "2. Review CCTV footage covering the engineering workstation.\n"
            "3. Audit operator smart card access logs at the facility badge reader."
        ),
        "cyber_physical_risk": (
            "An unauthorized person or malware might be sitting at the physical engineering console attempting to gain control "
            "of the industrial software that programs safety shutdown logic."
        ),
        "recommended_action": (
            "1. Dispatch facility security to visually inspect the control room.\n"
            "2. Lock the operator workstation session remotely.\n"
            "3. Revoke the badge credentials until the employee re-verifies in person."
        )
    },
    "UNUSUAL_RDP_TRAFFIC": {
        "title": "Off-Hours Remote Desktop Session Detected",
        "what_happened": (
            "A remote desktop connection passed through the perimeter firewall into the industrial network outside of standard "
            "operating hours or scheduled maintenance windows."
        ),
        "why_dangerous": (
            "Remote access into the operations zone (Purdue Level 3) allows an external actor to bypass physical perimeter security "
            "and manipulate supervisory screens without on-site operator oversight."
        ),
        "propagation_path": (
            "Corporate ERP Network ➔ Industrial DMZ Firewall ➔ Remote Jump Host ➔ Engineering Workstation ➔ Operations Subnet."
        ),
        "operational_impact": (
            "Potential lateral movement across the plant network, configuration tampering, and unauthorized data exfiltration."
        ),
        "investigation_steps": (
            "1. Terminate the active VPN and RDP session immediately.\n"
            "2. Contact the vendor engineer to confirm if emergency maintenance was approved.\n"
            "3. Verify multi-factor authentication logs on the perimeter gateway."
        ),
        "cyber_physical_risk": (
            "Remote access into the operations zone (Purdue Level 3) allows an outsider to manipulate supervisory screens, "
            "silence alarms, and pivot deeper toward controllers."
        ),
        "recommended_action": (
            "1. Terminate the active VPN and RDP session immediately.\n"
            "2. Contact the vendor engineer to confirm if emergency maintenance was approved.\n"
            "3. Enforce multi-factor verification on the DMZ jump host."
        )
    },
    "UNAUTHORIZED_ACCESS_ALERT": {
        "title": "Role-Based Access Control (RBAC) Violation Blocked",
        "what_happened": (
            "A user logged in under a lower-privileged role (such as standard Operator) attempted an engineering or administrative "
            "action (such as modifying PLC logic, downloading firmware, or altering firewall rules). IndustrialShield blocked the action."
        ),
        "why_dangerous": (
            "Separation of duties protects against accidental misconfiguration and malicious insider threats. Permitting arbitrary "
            "edits risks uploading unverified logic to live machinery."
        ),
        "propagation_path": (
            "Operator Workstation ➔ Supervisory HMI ➔ Engineering Protocol Port ➔ Core Turbine Controller."
        ),
        "operational_impact": (
            "Unauthorized parameter drift, invalid PID tuning values, and unapproved changes to emergency trip setpoints."
        ),
        "investigation_steps": (
            "1. Interview the active operator regarding the attempted action.\n"
            "2. Review the session audit trail to check for credential sharing.\n"
            "3. Confirm that control loop setpoints remain locked within nominal ranges."
        ),
        "cyber_physical_risk": (
            "Unauthorized configuration changes can disable safety interlocks or corrupt automated control logic, causing plant shutdowns."
        ),
        "recommended_action": (
            "1. Ensure the user is trained on separation of duties.\n"
            "2. Audit user privileges to determine if this was an accidental click or an intentional privilege escalation attempt."
        )
    },
    "SIS_BYPASS_ATTEMPT": {
        "title": "Safety Instrumented System (SIS) Tampering Detected",
        "what_happened": (
            "An external command attempted to override or bypass the Emergency Safety Instrumented System (SIS-01). The SIS is the "
            "last line of defense designed to autonomously shut down the plant in a catastrophic emergency."
        ),
        "why_dangerous": (
            "Disabling the SIS removes the fail-safe emergency brakes of the industrial plant. If steam pressure spikes, the safety "
            "valve might not open automatically, risking a catastrophic physical rupture."
        ),
        "propagation_path": (
            "Compromised Engineering Laptop ➔ Safety Network Port ➔ SIS-01 Autonomous Controller ➔ Emergency Dump Solenoids."
        ),
        "operational_impact": (
            "Loss of emergency shutdown protection, risk of boiler explosion, and severe worker safety hazards."
        ),
        "investigation_steps": (
            "1. High emergency: Sound internal plant cybersecurity alert.\n"
            "2. Physically inspect SIS-01 key switch and confirm it is locked in autonomous RUN mode.\n"
            "3. Physically disconnect any programming cables attached to the safety controller."
        ),
        "cyber_physical_risk": (
            "Disabling the SIS removes the fail-safe emergency brakes of the industrial plant. If steam pressure spikes, the safety "
            "valve might not open automatically, risking an explosion or major physical rupture."
        ),
        "recommended_action": (
            "1. High emergency: Sound internal plant cybersecurity alert.\n"
            "2. Physically turn the key switch on SIS-01 to autonomous lock.\n"
            "3. Disconnect engineering workstation cables from the safety subnet."
        )
    }
}


class AIExplainerEngine:
    """Provides plain-language AI explanations of security events with guaranteed fallback."""

    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")

    def explain(self, event_id: Optional[str] = None, incident_id: Optional[str] = None, custom_text: Optional[str] = None) -> ExplainEventResponse:
        target_event: Optional[SecurityEvent] = None
        target_incident: Optional[CorrelatedIncident] = None

        if incident_id:
            for inc in security_engine.get_correlated_incidents():
                if inc.id == incident_id:
                    target_incident = inc
                    break
        elif event_id:
            for evt in security_engine.get_events():
                if evt.id == event_id:
                    target_event = evt
                    break

        evt_type = target_event.event_type if target_event else "GENERIC_OT_ANOMALY"
        source_id = target_event.source_asset_id if target_event else "UNKNOWN"
        target_id = target_event.target_asset_id if target_event else "UNKNOWN"
        desc = target_event.description if target_event else (target_incident.summary if target_incident else custom_text or "General OT cybersecurity observation.")

        # Attempt to use Gemini API if API key is present
        if self.gemini_api_key:
            try:
                ai_result = self._call_gemini_api(evt_type, desc, source_id, target_id)
                if ai_result:
                    return ai_result
            except Exception as e:
                pass

        # Use Robust Intelligent Fallback Explainer
        return self._generate_fallback(evt_type, desc, source_id, target_id, target_incident)

    def _generate_fallback(self, evt_type: str, desc: str, source_id: str, target_id: Optional[str], incident: Optional[CorrelatedIncident]) -> ExplainEventResponse:
        """Deterministic, transparent plain-language explanation without needing cloud API keys."""
        if incident:
            return ExplainEventResponse(
                title=incident.title,
                what_happened=(
                    f"IndustrialShield correlated multiple individual security alerts into an active incident. "
                    f"{incident.summary}"
                ),
                why_dangerous=(
                    "When multiple security boundaries (perimeter, workstation verification, and controller communication) "
                    "are breached in sequence, it indicates an organized, targeted cyber-physical intrusion attempt."
                ),
                affected_asset=f"Multiple Assets: {', '.join(incident.involved_assets)}",
                propagation_path=f"Multi-tier traversal: {' ➔ '.join(incident.involved_assets)}",
                operational_impact="Imminent risk of controller state desynchronization and uncommanded machinery shutdown.",
                investigation_steps=(
                    f"1. Isolate the affected network segment.\n"
                    f"2. Inspect physical safety keys on {', '.join([a for a in incident.involved_assets if 'PLC' in a or 'SIS' in a])}.\n"
                    f"3. Follow recommendation: {incident.recommended_action}"
                ),
                cyber_physical_risk=(
                    "When multiple security boundaries (perimeter, workstation verification, and controller communication) "
                    "are crossed in rapid succession, it indicates an organized intrusion attempting to compromise real-time physical control."
                ),
                recommended_action=incident.recommended_action,
                technical_details={
                    "incident_id": incident.id,
                    "severity": incident.severity.value,
                    "involved_events": incident.involved_events,
                    "involved_assets": incident.involved_assets,
                    "detection_layer": "Correlation & Purdue Multi-Tier Inspection"
                },
                explainer_mode="Fallback Intelligent Rule-Based Engine (Deterministic)"
            )

        kb_entry = FALLBACK_KNOWLEDGE_BASE.get(evt_type)
        if kb_entry:
            title = kb_entry["title"]
            what_happened = kb_entry["what_happened"]
            why_dangerous = kb_entry["why_dangerous"]
            propagation_path = kb_entry["propagation_path"]
            operational_impact = kb_entry["operational_impact"]
            investigation_steps = kb_entry["investigation_steps"]
            cyber_physical_risk = kb_entry["cyber_physical_risk"]
            recommended_action = kb_entry["recommended_action"]
        else:
            title = f"Industrial Anomaly: {evt_type.replace('_', ' ').title()}"
            what_happened = f"An abnormal condition was detected on {source_id}: {desc}"
            why_dangerous = "Unexpected communications or protocol changes in operational zones can disrupt automated physical cycles."
            propagation_path = f"{source_id} ➔ Connected Controllers"
            operational_impact = "Potential process interruption or false sensor feedback to supervisory operators."
            investigation_steps = "Inspect controller logs, verify physical process readings, and isolate the source network port."
            cyber_physical_risk = "Abnormal activity in the industrial automation layer can disrupt continuous production cycles or cause sensor blinding."
            recommended_action = "Inspect controller logs, verify physical process readings, and isolate the source network port."

        affected_asset_label = f"{source_id}" + (f" targeting {target_id}" if target_id else "")

        return ExplainEventResponse(
            title=title,
            what_happened=what_happened,
            why_dangerous=why_dangerous,
            affected_asset=affected_asset_label,
            propagation_path=propagation_path,
            operational_impact=operational_impact,
            investigation_steps=investigation_steps,
            cyber_physical_risk=cyber_physical_risk,
            recommended_action=recommended_action,
            technical_details={
                "event_type": evt_type,
                "source_asset": source_id,
                "target_asset": target_id,
                "raw_description": desc,
                "purdue_stage_affected": asset_manager.get_asset(source_id).stage.value if asset_manager.get_asset(source_id) else "Operational Subnet"
            },
            explainer_mode="Fallback Intelligent Rule-Based Engine (Deterministic)"
        )

    def _call_gemini_api(self, evt_type: str, desc: str, source_id: str, target_id: Optional[str]) -> Optional[ExplainEventResponse]:
        import urllib.request
        
        prompt = (
            f"You are an industrial cybersecurity expert explaining an OT security alert to a non-technical factory manager.\n"
            f"Event Type: {evt_type}\n"
            f"Source Asset: {source_id}\n"
            f"Target Asset: {target_id}\n"
            f"Technical Description: {desc}\n\n"
            f"Please respond in pure JSON with the following keys:\n"
            f"title: (short friendly title)\n"
            f"what_happened: (simple 2-sentence explanation of what occurred without technical jargon)\n"
            f"why_dangerous: (why this specific action creates an operational danger)\n"
            f"affected_asset: (the asset affected)\n"
            f"propagation_path: (how this threat could reach other systems)\n"
            f"operational_impact: (how this impacts equipment or uptime)\n"
            f"investigation_steps: (concrete steps for the operator)\n"
            f"cyber_physical_risk: (how this affects physical factory machinery, worker safety, or production downtime)\n"
            f"recommended_action: (clear step-by-step guidance for plant engineers)\n"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
            candidate_text = result["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(candidate_text)
            return ExplainEventResponse(
                title=parsed.get("title", f"AI Analysis: {evt_type}"),
                what_happened=parsed.get("what_happened", desc),
                why_dangerous=parsed.get("why_dangerous", "Risk of unauthorized industrial actuation."),
                affected_asset=parsed.get("affected_asset", source_id),
                propagation_path=parsed.get("propagation_path", f"{source_id} to downstream controllers"),
                operational_impact=parsed.get("operational_impact", "Potential operational disruption."),
                investigation_steps=parsed.get("investigation_steps", "Inspect physical controller status and logs."),
                cyber_physical_risk=parsed.get("cyber_physical_risk", "Potential impact to plant safety and operational availability."),
                recommended_action=parsed.get("recommended_action", "Isolate compromised asset and verify controller states."),
                technical_details={
                    "event_type": evt_type,
                    "source_asset": source_id,
                    "target_asset": target_id,
                    "raw_description": desc
                },
                explainer_mode="AI (Gemini 1.5 Flash)"
            )


# Singleton instance
ai_explainer = AIExplainerEngine()
