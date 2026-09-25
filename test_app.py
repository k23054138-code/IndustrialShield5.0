import unittest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.main import app
from backend.assets import asset_manager
from backend.graph_engine import graph_engine
from backend.security_engine import security_engine
from backend.ai_explainer import ai_explainer
from backend.models import Role, Severity, AssetStatus


class IndustrialShieldTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertGreater(data["networkx_graph_nodes"], 10)
        print("[PASS] Health check endpoint passed.")

    def test_02_assets_and_availability(self):
        res = self.client.get("/api/assets")
        self.assertEqual(res.status_code, 200)
        assets = res.json()
        self.assertGreaterEqual(len(assets), 14)
        
        # Test toggle asset online/offline
        asset_id = "PLC-TURBINE-01"
        toggle_res = self.client.post(f"/api/assets/{asset_id}/toggle-status")
        self.assertEqual(toggle_res.status_code, 200)
        toggled_data = toggle_res.json()
        self.assertEqual(toggled_data["status"], "OFFLINE")

        # Toggle back online
        toggle_back = self.client.post(f"/api/assets/{asset_id}/toggle-status")
        self.assertEqual(toggle_back.json()["status"], "ONLINE")
        print("[PASS] Asset availability and online/offline toggle passed.")

    def test_03_circular_risk_gauge_calculation(self):
        res = self.client.get("/api/risk/overall")
        self.assertEqual(res.status_code, 200)
        risk = res.json()
        self.assertIn("overall_score", risk)
        self.assertIn("risk_level", risk)
        self.assertIn("color", risk)
        self.assertIn("stage_breakdown", risk)
        self.assertTrue(risk["color"].startswith("#"))
        self.assertGreaterEqual(risk["overall_score"], 0.0)
        self.assertLessEqual(risk["overall_score"], 100.0)
        print(f"[PASS] Circular risk detection: {risk['overall_score']}% ({risk['risk_level']}) with color {risk['color']}.")

    def test_04_networkx_graph_and_impact_analysis(self):
        # Topology
        res = self.client.get("/api/graph")
        self.assertEqual(res.status_code, 200)
        top = res.json()
        self.assertGreaterEqual(top["total_nodes"], 14)
        self.assertGreaterEqual(top["total_edges"], 14)

        # Impact analysis from Engineering Workstation to Safety System
        impact_res = self.client.post("/api/impact-analysis", json={
            "source_node": "ENG-WORKSTATION-01",
            "target_node": "SIS-01"
        })
        self.assertEqual(impact_res.status_code, 200)
        impact = impact_res.json()
        self.assertGreater(len(impact["exposure_paths"]), 0)
        self.assertGreater(impact["blast_radius_count"], 0)
        self.assertGreater(len(impact["mitigation_steps"]), 0)
        print(f"[PASS] NetworkX exposure paths discovered: {len(impact['exposure_paths'])} paths.")

    def test_05_safe_operator_verification(self):
        # 1. Valid Engineer Verification
        valid_res = self.client.post("/api/operator-verify", json={
            "badge_id": "BADGE-ENG-802",
            "pin_code": "5678",
            "workstation_id": "ENG-WORKSTATION-01"
        })
        self.assertEqual(valid_res.status_code, 200)
        v_data = valid_res.json()
        self.assertTrue(v_data["success"])
        self.assertEqual(v_data["assigned_role"], "engineer")
        self.assertIn("Safe Cryptographic Token", v_data["verification_method"])

        # 2. Rogue Badge (Should fail and generate security alert)
        invalid_res = self.client.post("/api/operator-verify", json={
            "badge_id": "BADGE-ROGUE-999",
            "pin_code": "0000",
            "workstation_id": "ENG-WORKSTATION-01"
        })
        self.assertEqual(invalid_res.status_code, 200)
        inv_data = invalid_res.json()
        self.assertFalse(inv_data["success"])
        self.assertTrue(inv_data["alert_generated"])
        print("[PASS] Safe operator verification (biometric-free) passed.")

    def test_06_rbac_enforcement_and_unauthorized_alert(self):
        # 1. Operator attempts to modify PLC logic (Blocked & Alert generated)
        blocked_res = self.client.post("/api/rbac/check-action", json={
            "role": "operator",
            "action": "modify_plc_logic",
            "target_asset_id": "PLC-TURBINE-01"
        })
        self.assertEqual(blocked_res.status_code, 200)
        b_data = blocked_res.json()
        self.assertFalse(b_data["allowed"])
        self.assertTrue(b_data["alert_generated"])

        # 2. Admin executes allowed config
        admin_res = self.client.post("/api/rbac/check-action", json={
            "role": "admin",
            "action": "modify_plc_logic",
            "target_asset_id": "PLC-TURBINE-01"
        })
        self.assertEqual(admin_res.status_code, 200)
        a_data = admin_res.json()
        self.assertTrue(a_data["allowed"])
        self.assertFalse(a_data["alert_generated"])
        print("[PASS] RBAC enforcement and UNAUTHORIZED_ACCESS_ALERT generation passed.")

    def test_07_event_correlation(self):
        res = self.client.get("/api/correlations")
        self.assertEqual(res.status_code, 200)
        corrs = res.json()
        self.assertGreater(len(corrs), 0)
        corr = corrs[0]
        self.assertIn("Correlated Incident", corr["title"])
        self.assertGreater(len(corr["involved_events"]), 0)
        print(f"[PASS] Event correlation passed: {corr['title']}.")

    def test_08_ai_and_fallback_explainer(self):
        # Test explain event endpoint with fallback mode
        explain_res = self.client.post("/api/ai/explain", json={
            "event_id": "EVT-1003"
        })
        self.assertEqual(explain_res.status_code, 200)
        exp = explain_res.json()
        self.assertIn("what_happened", exp)
        self.assertIn("cyber_physical_risk", exp)
        self.assertIn("recommended_action", exp)
        self.assertIn("explainer_mode", exp)
        print(f"[PASS] Plain-language explainer passed ({exp['explainer_mode']}).")

    def test_09_crypto_inspector(self):
        res = self.client.get("/api/crypto/inspect")
        self.assertEqual(res.status_code, 200)
        crypto = res.json()
        self.assertIn("credentials_demo", crypto)
        self.assertIn("encrypted_plc_config", crypto)
        self.assertIn("safety_statement", crypto)
        self.assertTrue(len(crypto["credentials_demo"]) >= 3)
        print("[PASS] Cryptographic inspection data passed.")

    def test_10_auth_login(self):
        # 1. Successful authentication
        res = self.client.post("/api/auth/login", json={
            "user_id": "engineer",
            "password": "engineer123",
            "face_verified": True
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["role"], "engineer")
        self.assertIsNotNone(data["session_token"])

        # 2. Failed authentication with wrong password
        fail_res = self.client.post("/api/auth/login", json={
            "user_id": "engineer",
            "password": "wrong_password",
            "face_verified": False
        })
        self.assertEqual(fail_res.status_code, 200)
        fail_data = fail_res.json()
        self.assertFalse(fail_data["success"])
        print("[PASS] User authentication endpoint passed.")


if __name__ == "__main__":
    unittest.main()
