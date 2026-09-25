# 🛡️ IndustrialShield - OT Cyber-Physical Defense Console

**IndustrialShield** is a safe, modular hackathon demonstration platform designed for industrial cybersecurity, Operational Technology (OT) asset monitoring, graph-based attack exposure path analysis, role-based access control, and transparent incident explanation.

---

## 🔒 Safety & Ethical Compliance Guarantee

* **Strictly Educational & Simulated:** No real PLC control, live malware, exploit payloads, or real industrial attacks are executed.
* **Biometric-Free Guarantee:** No real biometric data is collected, processed, uploaded, or stored.
* **Live Camera Demonstration:** The browser's webcam API (`navigator.mediaDevices.getUserMedia`) is used strictly for an in-browser visual demonstration. No images are saved, uploaded, or transmitted.
* **Demo / Simulated Face Verification:** Face verification is clearly designated as a simulated challenge authentication. If the camera is denied or unavailable, a safe demo fallback is provided so the application can always be demonstrated smoothly.

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

* **Cyber-Physical Operations Console:** `http://localhost:8000`
* **FastAPI Interactive API Documentation:** `http://localhost:8000/docs`

### 3. Run Automated Tests

```bash
python test_app.py
```

*(All 9 unit and integration tests pass cleanly in under 0.2s.)*

---

## 🔑 Login & Authentication Guide

When accessing the console, the user is presented with the **IndustrialShield Authentication Console**.

### Pre-Configured Test Accounts

* **Engineer Account:** User ID: `engineer` | Password: `engineer123` | Marcus Vance
* **Operator Account:** User ID: `operator` | Password: `operator123` | Sarah Connor
* **Admin Account:** User ID: `admin` | Password: `admin123` | Elena Rostova

*(Quick Fill buttons are also available on the login screen.)*

### Authentication Flow

1. **User ID & Password:** The user enters their credentials.
2. **Start Camera:** The browser requests camera permission and displays the live webcam stream.
3. **Verify Face:** The system performs a simulated face verification process with a scanning animation.
4. **Demo Disclaimer:** The system clearly displays that face verification is simulated and that no biometric data is stored.
5. **Safe Demo Fallback:** If camera access is denied or unavailable, the user can use the fallback option without interrupting the demonstration.
6. **Authenticate & Enter Console:** The user enters the multi-dashboard console and the Overview Dashboard is displayed.

---

## 🧭 Multi-Dashboard Sidebar Architecture

The application contains dedicated dashboard panes and a logout control through the left sidebar.

### 1. 📊 Overview Dashboard

Displays:

* Overall operational security posture
* Total OT assets
* Online / Offline assets
* Active threats
* Compromised assets
* Circular Risk Detection Gauge
* Recent security events

### 2. 🏭 OT Asset Monitoring

Monitors **14 simulated OT assets** distributed across Purdue Model Levels 0–4.

Features include:

* Asset identification
* Purdue Level classification
* Online / Offline status
* Compromise status
* Asset risk information

### 3. 🚨 Threat Detection

Displays simulated industrial security telemetry.

Features include:

* Threat events
* Severity levels
* Low, Medium, High, and Critical classifications
* Simulated OT attack scenario triggers
* Threat status monitoring

### 4. 🔬 Impact Analysis & Graph

Provides graph-based analysis of the simulated industrial environment.

Features include:

* NetworkX directed graph topology
* Industrial asset relationships
* Attack exposure path calculation
* Blast-radius tracking
* Risk propagation visualization
* **Industrial Impact Analysis Graph**
* Interactive bar chart showing risk / impact scores for assets

The graph helps demonstrate how a security event affecting one asset could potentially expose connected assets in the simulated environment.

### 5. 🤖 AI Threat Explanation

Converts technical OT security alerts into simple operational explanations.

The explanation answers six important questions:

1. **What happened?**
2. **Why is it dangerous?**
3. **Which asset is affected?**
4. **How could the threat propagate?**
5. **What is the possible operational impact?**
6. **What should the operator investigate?**

The system provides a transparent rule-based explanation engine so that the demonstration can operate without depending on an external AI service.

If a Gemini integration is configured in the application through `GEMINI_API_KEY`, it can be used according to the implemented configuration.

### 6. 🔗 Incident Correlation

Correlates multiple simulated security events into a meaningful incident timeline.

Examples include:

* Physical / badge anomalies
* Unauthorized access events
* OT protocol activity
* Related security alerts
* Multi-stage event sequences

This helps demonstrate how separate events can be connected to identify a larger security incident.

### 7. 🛡️ Access Control / RBAC

Provides role-based access control for different industrial users.

Features include:

* Engineer permissions
* Operator permissions
* Admin permissions
* Command execution testing
* Separation-of-duties matrix
* Unauthorized command detection
* Automatic `UNAUTHORIZED_ACCESS_ALERT` event generation

### 8. 🔐 Cryptographic Inspection

Demonstrates security mechanisms used to protect sensitive information.

Features include:

* Salted SHA-256 operator PIN hashing
* Fernet-based encrypted PLC safety configuration
* Cryptographic inspection and verification demonstration

All cryptographic operations are demonstrated using simulated application data.

### 9. ⚙️ System Settings

Provides system and application monitoring features.

Displays:

* System health telemetry
* Graph node metrics
* Graph edge metrics
* Current system state
* Baseline reset functionality

### 10. 🚪 Logout

Clears the current session and returns the user to the authentication console.

---

## 📁 File Structure & Explanation of Every File

| File Path                    | Role                             | Simple Language Explanation                                                                                                                     |
| :--------------------------- | :------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| `run.py`                     | **Launcher Script**              | Starts the FastAPI application on `http://localhost:8000` with live reload.                                                                     |
| `test_app.py`                | **Test Suite**                   | Contains automated unit and integration tests for application functionality.                                                                    |
| `requirements.txt`           | **Dependencies**                 | Contains the Python packages required by the project such as FastAPI, Uvicorn, NetworkX, Pydantic, Cryptography, and HTTPX.                     |
| `backend/main.py`            | **FastAPI Server**               | Provides REST API endpoints such as `/api/auth/login`, `/api/assets`, `/api/risk/overall`, and `/api/impact-analysis`, and serves the frontend. |
| `backend/models.py`          | **Data Schemas**                 | Defines Pydantic data models used for consistent and validated API data.                                                                        |
| `backend/assets.py`          | **Asset & Risk Manager**         | Manages the 14 simulated OT assets, Purdue Levels 0–4, availability status, compromise status, and risk calculations.                           |
| `backend/graph_engine.py`    | **NetworkX Graph Engine**        | Uses NetworkX directed graphs to model industrial network relationships, calculate exposure paths, and determine blast radius.                  |
| `backend/security_engine.py` | **Security & RBAC Engine**       | Handles authentication, role-based permission checks, unauthorized access alerts, event correlation, and cryptographic inspection.              |
| `backend/ai_explainer.py`    | **AI Threat Explanation Engine** | Converts technical OT security alerts into six simple operational explanations using a deterministic rule-based fallback.                       |
| `frontend/index.html`        | **Application Markup**           | Contains the login / camera interface, sidebar navigation, dashboards, and Impact Analysis interface.                                           |
| `frontend/styles.css`        | **Cyber Theme Styling**          | Provides the industrial dark theme, camera HUD styling, animated risk gauge, charts, and responsive layouts.                                    |
| `frontend/app.js`            | **Frontend Controller**          | Handles client-side logic, camera streaming, simulated face scanning, dashboard navigation, topology rendering, and impact chart visualization. |
| `README.md`                  | **Documentation**                | Provides the project overview, setup instructions, architecture, safety information, and file explanations.                                     |

---

## 🏗️ Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* NetworkX
* Cryptography

### Frontend

* HTML5
* CSS3
* JavaScript
* Browser Webcam API
* Canvas-based visualizations

### Security Concepts Demonstrated

* Operational Technology (OT) Security
* Purdue Model
* Asset Monitoring
* Threat Detection
* Attack Exposure Analysis
* Blast Radius Analysis
* Risk Analysis
* Role-Based Access Control (RBAC)
* Incident Correlation
* Cryptographic Protection
* AI-Assisted Threat Explanation

---

## 🧠 Project Architecture

```text
                         ┌─────────────────────────┐
                         │       User / Operator    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   IndustrialShield UI   │
                         │ HTML / CSS / JavaScript │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      FastAPI Backend    │
                         └────────────┬────────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
    ┌────────────────┐      ┌──────────────────┐      ┌─────────────────┐
    │ OT Asset Engine│      │ Security Engine  │      │ Graph Engine    │
    │ Asset + Risk   │      │ RBAC + Events    │      │ NetworkX Graph  │
    └────────────────┘      └──────────────────┘      └─────────────────┘
             │                        │                        │
             └────────────────────────┼────────────────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ AI Threat Explanation   │
                         │ Rule-Based Explanation  │
                         └─────────────────────────┘
```

---

## 🛡️ Safe Simulation Approach

IndustrialShield is designed specifically as a **safe cybersecurity demonstration platform**.

The project does **not**:

* Control real industrial equipment
* Attack real PLCs
* Deploy malware
* Execute exploit payloads
* Perform real unauthorized access
* Store biometric information
* Send webcam images to external servers

Instead, the system uses **simulated OT assets, simulated security events, simulated attack scenarios, and controlled application logic** to demonstrate cybersecurity concepts.

---

## 🎯 Project Objective

The main objective of IndustrialShield is to demonstrate how an integrated cybersecurity console can help an operator understand:

**Asset → Threat → Exposure Path → Impact → Explanation → Response**

The platform combines OT monitoring, graph-based impact analysis, access control, incident correlation, cryptographic inspection, and explainable threat analysis into one demonstration environment.

---

## 📌 Hackathon Demonstration Flow

A typical demonstration can follow this sequence:

1. Login to the IndustrialShield console.
2. Demonstrate the safe camera authentication flow.
3. Open the **OT Asset Monitoring** dashboard.
4. Show the simulated industrial assets and Purdue Levels.
5. Open **Threat Detection** and demonstrate a simulated security event.
6. Open **Impact Analysis** to show the affected asset and graph relationships.
7. Demonstrate the **AI Threat Explanation** to explain the alert in simple language.
8. Open **Incident Correlation** to show related events.
9. Demonstrate **RBAC** by testing authorized and unauthorized commands.
10. Show the **Cryptographic Inspection** dashboard.
11. Use **System Settings** to demonstrate system health and baseline reset.
12. Logout safely.

---

## ✅ Key Advantages

* Safe and fully simulated
* Designed for educational and hackathon demonstration
* Combines IT/OT cybersecurity concepts
* Provides visual industrial asset monitoring
* Uses graph-based exposure analysis
* Provides explainable threat information
* Demonstrates RBAC and separation of duties
* Demonstrates incident correlation
* Demonstrates cryptographic protection
* Includes automated application testing
* Provides a clear and user-friendly dashboard

---

## ⚠️ Disclaimer

IndustrialShield is a **hackathon demonstration and educational simulation**.

All industrial assets, security events, attack scenarios, authentication demonstrations, and operational impacts shown by the application are simulated for safe demonstration purposes.
