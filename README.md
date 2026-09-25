# 🛡️ IndustrialShield - OT Cyber-Physical Defense Console

**IndustrialShield** is a safe, modular hackathon demonstration platform designed for industrial cybersecurity, operational technology (OT) asset monitoring, graph-based attack exposure path analysis, role-based access control, and transparent incident explanation.

---

## 🔒 Safety & Ethical Compliance Guarantee
- **Strictly Educational & Simulated:** No real PLC control, no live malware, no exploit payloads, and no real industrial attacks are executed.
- **Biometric-Free Guarantee:** Strictly **zero real biometric data** is collected, processed, uploaded, or stored.
- **Live Camera Demonstration:** The browser's webcam API (`navigator.mediaDevices.getUserMedia`) is used strictly for an in-browser visual demonstration. No images are saved, uploaded, or transmitted.
- **Demo / Simulated Face Verification:** Clearly designated as simulated challenge authentication. If the camera is denied or unavailable, a safe demo fallback is provided so the entire application can always be demonstrated smoothly.

---

## 🚀 Quick Start Guide

### 1. Requirements & Installation
Ensure you have Python 3.10+ installed.

```bash
cd C:\Users\KALPANA\.gemini\antigravity\scratch\IndustrialShield
python -m pip install -r requirements.txt
```

### 2. Launch the Application
Run the launcher script:
```bash
python run.py
```

Open your browser at:
- **Cyber-Physical Operations Console:** [http://localhost:8000](http://localhost:8000)
- **FastAPI Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run Automated Tests
```bash
python test_app.py
```
*(All 10 unit and integration tests pass cleanly in under 0.2s)*

---

## 🔑 Login & Authentication Guide

When accessing the console, the user is presented with the **IndustrialShield Authentication Console**:

### Pre-Configured Test Accounts:
- **Engineer Account (Recommended):** User ID: `engineer` | Password: `engineer123` (Marcus Vance)
- **Operator Account:** User ID: `operator` | Password: `operator123` (Sarah Connor)
- **Admin Account:** User ID: `admin` | Password: `admin123` (Elena Rostova)
*(Or click the Quick Fill buttons at the top of the login terminal)*

### Authentication Flow:
1. **User ID & Password:** Entered into credentials pane.
2. **Start Camera:** Requests browser camera permission to open the live webcam stream in the target reticle frame.
3. **Verify Face:** Simulates face verification with a scanning animation ("Scanning...", "Verifying...", "Verification Complete") and renders the clear disclaimer:
   > *"Face verification successful — Demo Mode. Demo Mode — Face verification is simulated. No biometric data is stored."*
4. **Safe Demo Fallback:** If camera access is denied or unavailable on the machine, click the fallback link to bypass the camera without crashing the demonstration.
5. **Authenticate & Enter Console:** Redirects to the multi-dashboard console and loads the **Overview Dashboard**.

---

## 🧭 Multi-Dashboard Sidebar Architecture

The application is structured into 9 dedicated dashboard panes and a logout control via the left sidebar:

1. **📊 Overview Dashboard:** Operational posture, key metric cards (Total Assets, Online/Offline, Active Threats, Compromised Assets), the Circular Risk Detection Gauge, and recent security events.
2. **🏭 OT Asset Monitoring:** 14 Purdue Model assets across Levels 0–4. Online/Offline availability toggles and compromise flags.
3. **🚨 Threat Detection:** Live simulated threat telemetry, severity badges (Low, Medium, High, Critical), and OT attack scenario injection triggers.
4. **🔬 Impact Analysis & Graph:**
   - NetworkX directed graph topology visualizer.
   - Attack exposure path calculation and blast radius tracking.
   - **Industrial Impact Analysis Graph:** Interactive bar chart at the bottom visualizing risk/impact scores per asset with interactive hover tooltips.
5. **🤖 AI Threat Explanation:** Transparent plain-language threat explanations answering:
   - *What happened?*
   - *Why is it dangerous?*
   - *Which asset is affected?*
   - *How could the threat propagate?*
   - *What is the possible operational impact?*
   - *What should the operator investigate?*
   *(Uses Gemini if `GEMINI_API_KEY` is present; otherwise clearly displays the Fallback Intelligent Rule-Based Engine).*
6. **🔗 Incident Correlation:** Multi-vector event sequence timelines linking physical/badge anomalies with unauthorized Modbus/OT protocol manipulation.
7. **🛡️ Access Control / RBAC:** Interactive command execution tester, separation of duties matrix, and auto-logging of `UNAUTHORIZED_ACCESS_ALERT` events.
8. **🔐 Cryptographic Inspection:** Demonstrates salted SHA-256 operator PIN hashes and AES-128 Fernet encrypted PLC safety configuration logic.
9. **⚙️ System Settings:** System health telemetry, graph nodes/edges metrics, and baseline reset button.
10. **🚪 Logout:** Clears session and returns to the authentication console.

---

## 📁 File Structure & Explanation of Every File

| File Path | Role | Simple Language Explanation |
| :--- | :--- | :--- |
| `run.py` | **Launcher Script** | Starts the FastAPI application on `http://localhost:8000` with live reload. |
| `test_app.py` | **Test Suite** | 10 automated unit & integration tests validating health, assets, circular risk gauge, NetworkX paths, RBAC enforcement, event correlation, AI fallback, crypto inspector, and authentication. |
| `requirements.txt` | **Dependencies** | Python packages: `fastapi`, `uvicorn`, `networkx`, `pydantic`, `cryptography`, `httpx`. |
| `backend/main.py` | **FastAPI Server** | Exposes REST endpoints (`/api/auth/login`, `/api/assets`, `/api/risk/overall`, `/api/impact-analysis`, etc.) and serves frontend static files. |
| `backend/models.py` | **Data Schemas** | Pydantic data models ensuring consistent and validated data transfer across the API. |
| `backend/assets.py` | **Asset & Risk Manager** | Manages 14 OT assets across Purdue Levels 0–4, availability tracking (online/offline), and the dynamic circular risk calculation. |
| `backend/graph_engine.py` | **NetworkX Graph Engine** | Uses NetworkX directed graphs to model industrial network links, calculate shortest attack exposure paths, and determine blast radii. |
| `backend/security_engine.py` | **Security & RBAC Engine** | Manages authentication, RBAC permission checks, automatic generation of `UNAUTHORIZED_ACCESS_ALERT` events, multi-stage event correlation, and cryptographic inspection. |
| `backend/ai_explainer.py` | **AI Explainer Engine** | Translates technical OT alerts into 6 clear plain-language operational answers with instant deterministic fallback. |
| `frontend/index.html` | **Application Markup** | User interface markup containing the Login/Camera terminal, left sidebar navigation, the 9 dedicated dashboards, and the Impact Analysis Graph. |
| `frontend/styles.css` | **Cyber Theme Styling** | High-contrast industrial dark theme, camera HUD reticle styling, animated circular SVG risk gauge, and responsive layouts. |
| `frontend/app.js` | **Frontend Controller** | Coordinates client-side logic, camera stream handling, simulated face scanning, sidebar routing, NetworkX canvas topology rendering, and interactive impact bar chart drawing. |
| `README.md` | **Documentation** | Complete operational walkthrough and architecture guide. |
