// IndustrialShield - Multi-Dashboard Cybersecurity Controller
let plantAssets = [];
let topologyData = { nodes: [], edges: [] };
let activeExposurePaths = [];
let allEvents = [];
let allIncidents = [];
let currentUser = null;
let webcamStream = null;
let faceVerified = false;

const CIRCUMFERENCE = 2 * Math.PI * 66; // ~414.69 for r=66

document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  checkExistingSession();
  setupChartHover();
  
  // Auto-refresh operational metrics every 10 seconds if logged in
  setInterval(() => {
    if (currentUser) {
      refreshData();
    }
  }, 10000);
});

// ==============================================================
// 1. AUTHENTICATION & WEBCAM CONTROLLER
// ==============================================================

function quickFillAccount(userId, password) {
  const uidInput = document.getElementById("loginUserId");
  const pwdInput = document.getElementById("loginPassword");
  const preview = document.getElementById("loginRolePreview");
  
  if (uidInput) uidInput.value = userId;
  if (pwdInput) pwdInput.value = password;
  
  if (preview) {
    const roleText = userId.toUpperCase();
    preview.innerHTML = `Auto-selected <strong>${roleText}</strong> role credentials`;
  }
}

async function startCamera() {
  const video = document.getElementById("loginWebcam");
  const statusBadge = document.getElementById("cameraStatusBadge");
  const placeholder = document.getElementById("cameraPlaceholderText");

  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error("Webcam API not supported in this browser environment.");
    }

    webcamStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" }
    });

    if (video) {
      video.srcObject = webcamStream;
      video.play();
    }

    if (statusBadge) {
      statusBadge.textContent = "Camera Active";
      statusBadge.className = "status-badge status-active";
    }

    if (placeholder) placeholder.classList.add("hidden");

  } catch (err) {
    console.warn("Camera access error:", err);
    if (statusBadge) {
      statusBadge.textContent = "Camera access was denied or unavailable.";
      statusBadge.className = "status-badge status-error";
    }
    showFaceResult(
      "Camera access was denied or unavailable.",
      "Camera hardware not found or permission was denied. You can use 'Safe Demo Fallback' to continue with the hackathon demonstration.",
      "error"
    );
  }
}

function stopCamera() {
  const video = document.getElementById("loginWebcam");
  const statusBadge = document.getElementById("cameraStatusBadge");
  const placeholder = document.getElementById("cameraPlaceholderText");
  const scanLine = document.getElementById("scanLine");

  if (webcamStream) {
    webcamStream.getTracks().forEach(track => track.stop());
    webcamStream = null;
  }

  if (video) {
    video.srcObject = null;
  }

  if (statusBadge) {
    statusBadge.textContent = "Camera Standby";
    statusBadge.className = "status-badge status-standby";
  }

  if (placeholder) placeholder.classList.remove("hidden");
  if (scanLine) scanLine.classList.add("hidden");
}

function verifyFaceDemo() {
  const scanLine = document.getElementById("scanLine");
  const statusBadge = document.getElementById("cameraStatusBadge");

  if (scanLine) scanLine.classList.remove("hidden");
  if (statusBadge) {
    statusBadge.textContent = "Scanning...";
    statusBadge.className = "status-badge status-standby";
  }

  showFaceResult(
    "Scanning operator visual frame...",
    "Analyzing biometric boundary alignment (Simulated)...",
    "info"
  );

  setTimeout(() => {
    if (statusBadge) statusBadge.textContent = "Verifying cryptographic token...";
  }, 900);

  setTimeout(() => {
    if (scanLine) scanLine.classList.add("hidden");
    if (statusBadge) {
      statusBadge.textContent = "Verification Complete";
      statusBadge.className = "status-badge status-active";
    }

    faceVerified = true;
    showFaceResult(
      "Face verification successful — Demo Mode",
      "Demo Mode — Face verification is simulated. No biometric data is stored.",
      "success"
    );
  }, 2000);
}

function bypassCameraDemo() {
  faceVerified = true;
  const statusBadge = document.getElementById("cameraStatusBadge");
  if (statusBadge) {
    statusBadge.textContent = "Demo Verified (Bypass)";
    statusBadge.className = "status-badge status-active";
  }

  showFaceResult(
    "Face verification successful — Demo Mode",
    "Demo Mode — Face verification is simulated. No biometric data is stored. Camera access was bypassed for hackathon presentation.",
    "success"
  );
}

function showFaceResult(title, message, type) {
  const banner = document.getElementById("faceVerifyResult");
  if (!banner) return;

  banner.classList.remove("hidden");
  banner.className = `face-result-banner ${type}`;
  banner.innerHTML = `<strong>${title}</strong><br/><span>${message}</span>`;
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  const userId = document.getElementById("loginUserId")?.value.trim();
  const password = document.getElementById("loginPassword")?.value.trim();
  const feedback = document.getElementById("loginFeedback");

  if (!userId || !password) {
    showLoginError("Please enter both User ID and Password.");
    return;
  }

  if (!faceVerified) {
    showLoginError("Please complete Demo Face Verification (or click 'Safe Demo Fallback') before logging in.");
    return;
  }

  if (feedback) feedback.classList.add("hidden");

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        password: password,
        face_verified: faceVerified
      })
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      showLoginError(data.message || "Invalid credentials. Authentication rejected.");
      return;
    }

    // Login successful
    currentUser = {
      userId: data.user_id,
      name: data.operator_name || "Operator",
      role: data.role || "engineer",
      token: data.session_token,
      permissions: data.permissions || []
    };

    sessionStorage.setItem("industrial_shield_user", JSON.stringify(currentUser));
    stopCamera();
    activateAppSession();

  } catch (err) {
    console.error("Login request error:", err);
    showLoginError("Network connection error during authentication.");
  }
}

function showLoginError(msg) {
  const feedback = document.getElementById("loginFeedback");
  if (feedback) {
    feedback.classList.remove("hidden");
    feedback.className = "feedback-box error";
    feedback.textContent = msg;
  }
}

function checkExistingSession() {
  const saved = sessionStorage.getItem("industrial_shield_user");
  if (saved) {
    try {
      currentUser = JSON.parse(saved);
      activateAppSession();
    } catch (e) {
      sessionStorage.removeItem("industrial_shield_user");
    }
  }
}

function activateAppSession() {
  const loginView = document.getElementById("loginView");
  const appView = document.getElementById("appView");

  if (loginView) loginView.classList.add("hidden");
  if (appView) appView.classList.remove("hidden");

  // Update profile badges in sidebar and top status bar
  updateUserUI();

  // Load all dashboard operational data
  loadAllData();

  // Open default overview dashboard
  navigateToPage("dash-overview");
}

function updateUserUI() {
  if (!currentUser) return;

  const nameEl = document.getElementById("sidebarUserName");
  const roleEl = document.getElementById("sidebarUserRole");
  const avatarEl = document.getElementById("sidebarUserAvatar");
  const topRoleEl = document.getElementById("topRoleBadge");

  if (nameEl) nameEl.textContent = currentUser.name;
  if (roleEl) {
    roleEl.textContent = currentUser.role.toUpperCase();
    roleEl.className = `role-badge role-${currentUser.role}`;
  }
  if (topRoleEl) {
    topRoleEl.textContent = currentUser.role.toUpperCase();
    topRoleEl.className = `role-badge role-${currentUser.role}`;
  }
  if (avatarEl) {
    const initials = currentUser.name.split(" ").map(n => n[0]).join("").substring(0, 2);
    avatarEl.textContent = initials.toUpperCase() || "OP";
  }
}

function handleLogout() {
  stopCamera();
  currentUser = null;
  faceVerified = false;
  sessionStorage.removeItem("industrial_shield_user");

  const loginView = document.getElementById("loginView");
  const appView = document.getElementById("appView");
  const feedback = document.getElementById("loginFeedback");
  const faceResult = document.getElementById("faceVerifyResult");

  if (appView) appView.classList.add("hidden");
  if (loginView) loginView.classList.remove("hidden");

  if (feedback) feedback.classList.add("hidden");
  if (faceResult) faceResult.classList.add("hidden");

  const pwdInput = document.getElementById("loginPassword");
  if (pwdInput) pwdInput.value = "";
}


// ==============================================================
// 2. SIDEBAR MULTI-DASHBOARD NAVIGATION
// ==============================================================

const PAGE_METADATA = {
  "dash-overview": { title: "Overview Dashboard", breadcrumb: "Operations &bull; Cyber-Physical Posture" },
  "dash-assets": { title: "OT Asset Monitoring", breadcrumb: "Purdue Reference Architecture &bull; Levels 0 to 4" },
  "dash-threats": { title: "Threat Detection", breadcrumb: "Live Operational Technology Telemetry Stream" },
  "dash-impact": { title: "Impact Analysis & Graph", breadcrumb: "NetworkX Exposure Traversal &bull; Industrial Impact Analysis" },
  "dash-ai-explain": { title: "AI Threat Explanation", breadcrumb: "Transparent Industrial Cybersecurity Reasoning" },
  "dash-correlation": { title: "Incident Correlation", breadcrumb: "Multi-Vector Industrial Incident Correlation" },
  "dash-rbac": { title: "Access Control / RBAC", breadcrumb: "Zero-Trust Role-Based Access Enforcement" },
  "dash-crypto": { title: "Cryptographic Inspection", breadcrumb: "Data Integrity &bull; Authenticated Encryption (SIL-3)" },
  "dash-settings": { title: "System Settings", breadcrumb: "Platform Telemetry &bull; Baseline Controls" }
};

function setupNavigation() {
  const navItems = document.querySelectorAll(".sidebar-menu .nav-item[data-page]");
  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const pageId = item.getAttribute("data-page");
      navigateToPage(pageId);
    });
  });

  // Search & filter in Asset Dashboard
  const searchInput = document.getElementById("assetSearchInput");
  const stageFilter = document.getElementById("stageFilterSelect");
  if (searchInput) searchInput.addEventListener("input", renderAssetsGrid);
  if (stageFilter) stageFilter.addEventListener("change", renderAssetsGrid);

  // Impact Run Button
  const btnImpact = document.getElementById("btnRunImpact");
  if (btnImpact) btnImpact.addEventListener("click", runImpactAnalysis);

  // Topology Canvas click
  const canvas = document.getElementById("topologyCanvas");
  if (canvas) canvas.addEventListener("click", handleCanvasClick);
}

function navigateToPage(pageId) {
  // Update sidebar active indicator
  const navItems = document.querySelectorAll(".sidebar-menu .nav-item");
  navItems.forEach(item => {
    if (item.getAttribute("data-page") === pageId) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  // Hide all dashboard panes and show target
  const panes = document.querySelectorAll(".dashboard-pane");
  panes.forEach(pane => {
    if (pane.id === pageId) {
      pane.classList.add("active");
    } else {
      pane.classList.remove("active");
    }
  });

  // Update top bar title and breadcrumbs
  const meta = PAGE_METADATA[pageId] || { title: "Console", breadcrumb: "Industrial Operations" };
  const titleEl = document.getElementById("currentPageTitle");
  const breadEl = document.getElementById("currentPageBreadcrumb");
  if (titleEl) titleEl.textContent = meta.title;
  if (breadEl) breadEl.innerHTML = meta.breadcrumb;

  // Specific triggers when switching dashboards
  if (pageId === "dash-impact") {
    setTimeout(() => {
      drawTopologyCanvas();
      drawImpactBarChart();
    }, 50);
  } else if (pageId === "dash-ai-explain") {
    populateAiEventDropdown();
  }
}


// ==============================================================
// 3. OPERATIONAL DATA LOADING
// ==============================================================

async function loadAllData() {
  await Promise.all([
    loadRiskData(),
    loadAssets(),
    loadTopology(),
    loadEvents(),
    loadCorrelations(),
    loadCryptoData()
  ]);
  populateImpactDropdowns();
  populateAiEventDropdown();
}

async function refreshData() {
  await Promise.all([
    loadRiskData(),
    loadEvents(),
    loadCorrelations()
  ]);
}


// ==============================================================
// 4. OVERVIEW DASHBOARD & CIRCULAR RISK GAUGE
// ==============================================================

async function loadRiskData() {
  try {
    const res = await fetch("/api/risk/overall");
    if (!res.ok) return;
    const data = await res.json();

    // 1. Circular Gauge Progress & Color
    const score = data.overall_score;
    const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
    const circle = document.getElementById("gaugeProgress");
    if (circle) {
      circle.style.strokeDashoffset = offset;
      circle.style.stroke = data.color;
    }

    const gaugeVal = document.getElementById("gaugeValue");
    if (gaugeVal) gaugeVal.textContent = Math.round(score);

    const gaugeStatus = document.getElementById("gaugeStatusText");
    if (gaugeStatus) gaugeStatus.textContent = data.risk_level + " RISK";

    // 2. Risk Pills in Overview & Top Status Bar
    const topRiskPill = document.getElementById("topRiskPill");
    const overviewRiskPill = document.getElementById("overviewRiskPill");
    const pillText = `${data.risk_level.toUpperCase()} RISK`;
    const pillClass = `risk-pill pill-${data.risk_level.toLowerCase()}`;

    if (topRiskPill) {
      topRiskPill.textContent = pillText;
      topRiskPill.className = pillClass;
    }
    if (overviewRiskPill) {
      overviewRiskPill.textContent = pillText;
      overviewRiskPill.className = pillClass;
    }

    // 3. Metric Cards
    setElText("metricTotalAssets", data.total_assets);
    setElText("metricOnlineAssets", data.online_count);
    setElText("metricOfflineAssets", data.offline_count);
    setElText("metricActiveThreats", data.active_threat_count);
    setElText("metricCompromisedAssets", data.compromised_count);
    setElText("topOnlineCounter", `${data.online_count} / ${data.total_assets}`);
    setElText("sidebarThreatCount", data.active_threat_count);

    // 4. Risk Analysis Summary
    const summary = document.getElementById("riskAnalysisSummary");
    if (summary) summary.textContent = data.analysis_summary;

    // Redraw impact bar chart if it's visible
    drawImpactBarChart();

  } catch (err) {
    console.error("Error loading risk posture:", err);
  }
}

function setElText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}


// ==============================================================
// 5. OT ASSET MONITORING DASHBOARD
// ==============================================================

async function loadAssets() {
  try {
    const res = await fetch("/api/assets");
    if (!res.ok) return;
    plantAssets = await res.json();
    renderAssetsGrid();
    renderStageSummaryPills();
  } catch (err) {
    console.error("Error loading assets:", err);
  }
}

function renderStageSummaryPills() {
  const container = document.getElementById("stagePillsRow");
  if (!container) return;

  const stages = [
    "Level 4: Enterprise Network",
    "Level 3.5: Industrial DMZ",
    "Level 3: Operations & SCADA",
    "Level 2: Supervisory Control",
    "Level 1: Basic Control & Safety",
    "Level 0: Physical Field Devices"
  ];

  container.innerHTML = stages.map(st => {
    const inStage = plantAssets.filter(a => a.stage === st);
    const online = inStage.filter(a => a.status === "ONLINE").length;
    const cleanName = st.split(":")[0];
    return `
      <div class="stage-pill-box">
        <span class="st-title">${cleanName}</span>
        <span class="st-count">${online}/${inStage.length} Online</span>
      </div>
    `;
  }).join("");
}

function renderAssetsGrid() {
  const container = document.getElementById("assetsContainer");
  if (!container) return;

  const searchQuery = (document.getElementById("assetSearchInput")?.value || "").toLowerCase();
  const selectedStage = document.getElementById("stageFilterSelect")?.value || "ALL";

  container.innerHTML = "";

  const filtered = plantAssets.filter(a => {
    const matchSearch = a.id.toLowerCase().includes(searchQuery) ||
                        a.name.toLowerCase().includes(searchQuery) ||
                        a.ip_address.toLowerCase().includes(searchQuery);
    const matchStage = selectedStage === "ALL" || a.stage === selectedStage;
    return matchSearch && matchStage;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<div class="empty-state">No industrial assets found matching criteria.</div>`;
    return;
  }

  filtered.forEach(asset => {
    const card = document.createElement("div");
    card.className = `asset-card ${asset.status.toLowerCase()} ${asset.is_compromised ? 'compromised' : ''}`;

    const statusBadgeClass = asset.is_compromised ? "compromised" : asset.status.toLowerCase();
    const statusText = asset.is_compromised ? "COMPROMISED" : asset.status;

    card.innerHTML = `
      <div>
        <div class="asset-head">
          <div>
            <div class="asset-id">${asset.id}</div>
            <div class="asset-name">${asset.name}</div>
          </div>
          <span class="asset-stage-pill">${asset.stage.split(":")[0]}</span>
        </div>
        <div class="asset-meta-row">
          <span>IP: ${asset.ip_address}</span>
          <span>Proto: ${asset.protocol}</span>
        </div>
        <p class="asset-desc">${asset.description}</p>
      </div>

      <div class="asset-footer">
        <span class="status-badge ${statusBadgeClass}">
          <span class="dot ${asset.is_compromised ? 'dot-compromised' : (asset.status === 'ONLINE' ? 'dot-safe' : 'dot-offline')}"></span>
          ${statusText}
        </span>
        <div class="asset-actions">
          <button class="btn btn-sm btn-outline" onclick="toggleAssetStatus('${asset.id}')" title="Safe toggle online/offline availability">
            ${asset.status === 'ONLINE' ? 'Take Offline' : 'Bring Online'}
          </button>
          <button class="btn btn-sm ${asset.is_compromised ? 'btn-danger-outline' : 'btn-outline'}" onclick="toggleAssetCompromised('${asset.id}')" title="Toggle compromise flag">
            ${asset.is_compromised ? 'Clear' : 'Flag Comp'}
          </button>
          <button class="btn btn-sm btn-outline" onclick="inspectAssetExposure('${asset.id}')" title="Run impact analysis on this node">
            Impact &rarr;
          </button>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

async function toggleAssetStatus(assetId) {
  try {
    const res = await fetch(`/api/assets/${assetId}/toggle-status`, { method: "POST" });
    if (res.ok) {
      await loadAssets();
      await loadRiskData();
      await loadTopology();
      await loadEvents();
      drawImpactBarChart();
    }
  } catch (err) {
    console.error("Error toggling status:", err);
  }
}

async function toggleAssetCompromised(assetId) {
  try {
    const res = await fetch(`/api/assets/${assetId}/toggle-compromised`, { method: "POST" });
    if (res.ok) {
      await loadAssets();
      await loadRiskData();
      await loadTopology();
      await loadEvents();
      drawImpactBarChart();
    }
  } catch (err) {
    console.error("Error toggling compromise flag:", err);
  }
}

function inspectAssetExposure(assetId) {
  navigateToPage("dash-impact");
  const sourceSel = document.getElementById("impactSourceSelect");
  if (sourceSel) {
    sourceSel.value = assetId;
    runImpactAnalysis();
  }
}


// ==============================================================
// 6. THREAT DETECTION & SIMULATOR
// ==============================================================

async function loadEvents() {
  try {
    const res = await fetch("/api/events");
    if (!res.ok) return;
    allEvents = await res.json();
    setElText("metricTotalEvents", allEvents.length);
    renderThreatsStream(allEvents);
    renderRecentEventsPreview(allEvents.slice(0, 4));
  } catch (err) {
    console.error("Error loading events:", err);
  }
}

function renderRecentEventsPreview(events) {
  const container = document.getElementById("recentEventsPreview");
  if (!container) return;

  container.innerHTML = "";
  events.forEach(evt => {
    const row = document.createElement("div");
    row.className = "event-row";
    const sevClass = evt.severity === "CRITICAL" ? "text-danger" : (evt.severity === "HIGH" ? "text-warning" : "text-cyan");

    row.innerHTML = `
      <div class="event-top">
        <span class="event-type ${sevClass}">[${evt.severity}] ${evt.event_type}</span>
        <span class="event-time">${evt.timestamp}</span>
      </div>
      <div class="event-desc">${evt.description}</div>
      <div class="event-bottom">
        <span style="font-size: 0.7rem; color: var(--text-dim); font-family: var(--font-mono);">
          Src: ${evt.source_asset_id} ${evt.target_asset_id ? '➔ ' + evt.target_asset_id : ''}
        </span>
        <button class="btn btn-sm btn-outline" onclick="jumpToExplainEvent('${evt.id}')">Analyze &rarr;</button>
      </div>
    `;
    container.appendChild(row);
  });
}

function renderThreatsStream(events) {
  const container = document.getElementById("threatsStreamContainer");
  if (!container) return;

  container.innerHTML = "";
  events.forEach(evt => {
    const row = document.createElement("div");
    row.className = "event-row";
    const sevClass = evt.severity === "CRITICAL" ? "text-danger" : (evt.severity === "HIGH" ? "text-warning" : "text-cyan");

    row.innerHTML = `
      <div class="event-top">
        <span class="event-type ${sevClass}">[${evt.severity}] ${evt.event_type}</span>
        <span class="event-time">${evt.timestamp}</span>
      </div>
      <div class="event-desc">${evt.description}</div>
      <div class="event-bottom">
        <span style="font-size: 0.72rem; color: var(--text-dim); font-family: var(--font-mono);">
          Affected: ${evt.source_asset_id} ${evt.target_asset_id ? '➔ ' + evt.target_asset_id : ''} | Hash: ${evt.raw_payload_hash}
        </span>
        <button class="btn btn-sm btn-outline" onclick="jumpToExplainEvent('${evt.id}')">
          Explain with AI
        </button>
      </div>
    `;
    container.appendChild(row);
  });
}

async function triggerScenario(scenario) {
  try {
    const res = await fetch(`/api/simulate-event?scenario=${scenario}`, { method: "POST" });
    if (res.ok) {
      await loadRiskData();
      await loadEvents();
      await loadCorrelations();
      await loadTopology();
      drawImpactBarChart();
    }
  } catch (err) {
    console.error("Error triggering scenario:", err);
  }
}


// ==============================================================
// 7. IMPACT ANALYSIS DASHBOARD & IMPACT ANALYSIS GRAPH
// ==============================================================

async function loadTopology() {
  try {
    const res = await fetch("/api/graph");
    if (!res.ok) return;
    topologyData = await res.json();
    setElText("settingsGraphNodes", `${topologyData.total_nodes} Nodes`);
    setElText("settingsGraphEdges", `${topologyData.total_edges} Links`);
    drawTopologyCanvas();
  } catch (err) {
    console.error("Error loading topology:", err);
  }
}

const STAGE_Y_MAP = {
  "Level 4: Enterprise Network": 50,
  "Level 3.5: Industrial DMZ": 140,
  "Level 3: Operations & SCADA": 240,
  "Level 2: Supervisory Control": 340,
  "Level 1: Basic Control & Safety": 420,
  "Level 0: Physical Field Devices": 490
};

let nodePositions = {};

function drawTopologyCanvas() {
  const canvas = document.getElementById("topologyCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;

  ctx.clearRect(0, 0, width, height);

  // Background Purdue Zone Guides
  ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
  ctx.lineWidth = 1;
  for (const [stage, y] of Object.entries(STAGE_Y_MAP)) {
    ctx.beginPath();
    ctx.moveTo(10, y);
    ctx.lineTo(width - 10, y);
    ctx.stroke();

    ctx.fillStyle = "rgba(148, 163, 184, 0.25)";
    ctx.font = "10px JetBrains Mono, monospace";
    ctx.fillText(stage.split(":")[0], 14, y - 6);
  }

  // Calculate Node Positions
  const stageGroups = {};
  topologyData.nodes.forEach(node => {
    stageGroups[node.stage] = stageGroups[node.stage] || [];
    stageGroups[node.stage].push(node);
  });

  nodePositions = {};
  for (const [stage, nodes] of Object.entries(stageGroups)) {
    const y = STAGE_Y_MAP[stage] || 240;
    const spacing = width / (nodes.length + 1);
    nodes.forEach((node, index) => {
      nodePositions[node.id] = {
        x: spacing * (index + 1),
        y: y,
        node: node
      };
    });
  }

  // Draw Edges
  topologyData.edges.forEach(edge => {
    const src = nodePositions[edge.source];
    const tgt = nodePositions[edge.target];
    if (!src || !tgt) return;

    const isExposureEdge = activeExposurePaths.some(path => {
      for (let i = 0; i < path.length - 1; i++) {
        if (path[i] === edge.source && path[i + 1] === edge.target) return true;
      }
      return false;
    });

    ctx.beginPath();
    ctx.moveTo(src.x, src.y);
    ctx.lineTo(tgt.x, tgt.y);

    if (isExposureEdge) {
      ctx.strokeStyle = "#ef4444";
      ctx.lineWidth = 3.5;
      ctx.shadowColor = "#ef4444";
      ctx.shadowBlur = 10;
    } else {
      ctx.strokeStyle = "rgba(71, 85, 105, 0.4)";
      ctx.lineWidth = 1.2;
      ctx.shadowBlur = 0;
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
  });

  // Draw Nodes
  for (const [id, pos] of Object.entries(nodePositions)) {
    const node = pos.node;
    const radius = node.id === "SIS-01" ? 14 : 11;

    ctx.beginPath();
    ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);

    if (node.is_compromised) {
      ctx.fillStyle = "#ef4444";
      ctx.shadowColor = "#ef4444";
      ctx.shadowBlur = 12;
    } else if (node.status === "OFFLINE") {
      ctx.fillStyle = "#475569";
      ctx.shadowBlur = 0;
    } else if (node.id === "SIS-01") {
      ctx.fillStyle = "#06b6d4";
      ctx.shadowColor = "#06b6d4";
      ctx.shadowBlur = 8;
    } else {
      ctx.fillStyle = "#10b981";
      ctx.shadowBlur = 0;
    }

    ctx.fill();
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.shadowBlur = 0;

    ctx.fillStyle = "#f1f5f9";
    ctx.font = "10px JetBrains Mono, monospace";
    ctx.textAlign = "center";
    ctx.fillText(node.id, pos.x, pos.y + radius + 14);
  }
}

function handleCanvasClick(e) {
  const canvas = document.getElementById("topologyCanvas");
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;

  const clickX = (e.clientX - rect.left) * scaleX;
  const clickY = (e.clientY - rect.top) * scaleY;

  for (const [id, pos] of Object.entries(nodePositions)) {
    const dist = Math.hypot(clickX - pos.x, clickY - pos.y);
    if (dist <= 18) {
      const sourceSelect = document.getElementById("impactSourceSelect");
      if (sourceSelect) {
        sourceSelect.value = id;
        runImpactAnalysis();
      }
      break;
    }
  }
}

function populateImpactDropdowns() {
  const sourceSel = document.getElementById("impactSourceSelect");
  const targetSel = document.getElementById("impactTargetSelect");
  if (!sourceSel || !targetSel) return;

  sourceSel.innerHTML = "";
  targetSel.innerHTML = `<option value="">Auto-Detect Critical Targets (PLCs & SIS)</option>`;

  plantAssets.forEach(a => {
    const opt1 = document.createElement("option");
    opt1.value = a.id;
    opt1.textContent = `${a.id} (${a.name})`;
    sourceSel.appendChild(opt1);

    const opt2 = document.createElement("option");
    opt2.value = a.id;
    opt2.textContent = `${a.id} (${a.name})`;
    targetSel.appendChild(opt2);
  });

  sourceSel.value = "ENG-WORKSTATION-01";
}

async function runImpactAnalysis() {
  const sourceNode = document.getElementById("impactSourceSelect")?.value;
  const targetNode = document.getElementById("impactTargetSelect")?.value || null;
  const container = document.getElementById("impactResultsContainer");
  if (!sourceNode || !container) return;

  container.innerHTML = `<div class="empty-state">Computing NetworkX graph exposure traversal...</div>`;

  try {
    const res = await fetch("/api/impact-analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_node: sourceNode, target_node: targetNode })
    });

    if (!res.ok) return;
    const data = await res.json();

    activeExposurePaths = data.exposure_paths;
    drawTopologyCanvas();

    const pathsHtml = data.exposure_paths.length > 0
      ? data.exposure_paths.map(p => `<div class="path-box">${p.join(" ➔ ")}</div>`).join("")
      : `<div class="path-box">No direct exposure path to safety boundary detected.</div>`;

    const criticalListHtml = data.critical_assets_at_risk.length > 0
      ? data.critical_assets_at_risk.map(c => `<li>⚠️ ${c}</li>`).join("")
      : `<li>None</li>`;

    const mitigationsHtml = data.mitigation_steps.map(m => `<li>${m}</li>`).join("");

    container.innerHTML = `
      <div class="impact-stat-row">
        <span>Exposure Score:</span>
        <strong class="${data.exposure_risk_score > 70 ? 'text-danger' : 'text-warning'}">${data.exposure_risk_score} / 100</strong>
      </div>
      <div class="impact-stat-row">
        <span>Downstream Blast Radius:</span>
        <strong>${data.blast_radius_count} assets</strong>
      </div>

      <h5 style="margin-top: 12px; font-size: 0.82rem;">Computed Attack Exposure Paths:</h5>
      ${pathsHtml}

      <h5 style="margin-top: 12px; font-size: 0.82rem;">Critical Assets Exposed:</h5>
      <ul style="font-size: 0.78rem; margin-left: 18px; margin-top: 4px; color: #fca5a5;">
        ${criticalListHtml}
      </ul>

      <h5 style="margin-top: 12px; font-size: 0.82rem;">Actionable Mitigations:</h5>
      <ul style="font-size: 0.75rem; margin-left: 18px; margin-top: 4px; color: var(--text-muted); line-height: 1.4;">
        ${mitigationsHtml}
      </ul>
    `;

    // Redraw bar chart to reflect new exposure scores
    drawImpactBarChart();

  } catch (err) {
    console.error("Error running impact analysis:", err);
  }
}

// -------------------------------------------------------------
// IMPACT ANALYSIS BAR CHART (Required Interactive Graph)
// -------------------------------------------------------------
let barChartHitBoxes = [];

function drawImpactBarChart() {
  const canvas = document.getElementById("impactBarChartCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;

  ctx.clearRect(0, 0, width, height);
  barChartHitBoxes = [];

  const paddingLeft = 55;
  const paddingRight = 30;
  const paddingTop = 30;
  const paddingBottom = 65;

  const chartW = width - paddingLeft - paddingRight;
  const chartH = height - paddingTop - paddingBottom;

  // 1. Draw Grid Lines (0, 25, 50, 75, 100)
  ctx.strokeStyle = "rgba(71, 85, 105, 0.25)";
  ctx.lineWidth = 1;
  ctx.fillStyle = "rgba(148, 163, 184, 0.6)";
  ctx.font = "10px JetBrains Mono, monospace";
  ctx.textAlign = "right";

  const ticks = [0, 25, 50, 75, 100];
  ticks.forEach(tick => {
    const y = paddingTop + chartH - (tick / 100) * chartH;
    ctx.beginPath();
    ctx.moveTo(paddingLeft, y);
    ctx.lineTo(width - paddingRight, y);
    ctx.stroke();

    ctx.fillText(tick, paddingLeft - 8, y + 3);
  });

  // 2. Plot Bars for all assets
  if (!plantAssets || plantAssets.length === 0) return;

  const n = plantAssets.length;
  const barSpacing = chartW / n;
  const barWidth = Math.min(36, barSpacing * 0.65);

  plantAssets.forEach((asset, idx) => {
    const score = Math.min(100, Math.max(5, asset.risk_score));
    const barH = (score / 100) * chartH;
    const x = paddingLeft + (idx * barSpacing) + (barSpacing - barWidth) / 2;
    const y = paddingTop + chartH - barH;

    // Color based on risk level
    let barColor = "#10b981"; // Safe Green (<25)
    if (score >= 80) {
      barColor = "#ef4444"; // Crimson Red (Critical)
    } else if (score >= 56) {
      barColor = "#f97316"; // Orange (High)
    } else if (score >= 25) {
      barColor = "#f59e0b"; // Amber (Medium)
    }

    // Gradient bar
    const grad = ctx.createLinearGradient(0, y, 0, y + barH);
    grad.addColorStop(0, barColor);
    grad.addColorStop(1, "rgba(15, 23, 42, 0.5)");

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.roundRect(x, y, barWidth, barH, [4, 4, 0, 0]);
    ctx.fill();

    ctx.strokeStyle = barColor;
    ctx.lineWidth = 1.2;
    ctx.stroke();

    // Value label on top
    ctx.fillStyle = "#f1f5f9";
    ctx.font = "10px JetBrains Mono, monospace";
    ctx.textAlign = "center";
    ctx.fillText(Math.round(score), x + barWidth / 2, y - 6);

    // X-Axis Asset Label (rotated for readability)
    ctx.save();
    ctx.translate(x + barWidth / 2, paddingTop + chartH + 12);
    ctx.rotate(Math.PI / 4.5);
    ctx.fillStyle = asset.is_compromised ? "#ef4444" : (asset.status === "OFFLINE" ? "#64748b" : "#94a3b8");
    ctx.font = "9.5px JetBrains Mono, monospace";
    ctx.textAlign = "left";
    ctx.fillText(asset.id, 0, 0);
    ctx.restore();

    // Store Hitbox for Tooltip
    barChartHitBoxes.push({
      x: x,
      y: y,
      w: barWidth,
      h: barH,
      asset: asset,
      score: score
    });
  });
}

function setupChartHover() {
  const canvas = document.getElementById("impactBarChartCanvas");
  const tooltip = document.getElementById("chartTooltip");
  if (!canvas || !tooltip) return;

  canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const mouseX = (e.clientX - rect.left) * scaleX;
    const mouseY = (e.clientY - rect.top) * scaleY;

    let hovered = null;
    for (const b of barChartHitBoxes) {
      if (mouseX >= b.x && mouseX <= b.x + b.w && mouseY >= b.y && mouseY <= b.y + b.h) {
        hovered = b;
        break;
      }
    }

    if (hovered) {
      const a = hovered.asset;
      tooltip.classList.remove("hidden");
      tooltip.style.left = `${(e.clientX - rect.left) + 12}px`;
      tooltip.style.top = `${(e.clientY - rect.top) - 10}px`;

      const riskLvl = hovered.score >= 80 ? 'Critical' : (hovered.score >= 56 ? 'High' : (hovered.score >= 25 ? 'Medium' : 'Low'));
      tooltip.innerHTML = `
        <strong style="color:var(--accent-cyan);">${a.id}</strong><br/>
        <span style="font-size:0.75rem;">${a.name}</span><br/>
        <span style="color:var(--text-dim);">${a.stage.split(":")[0]}</span><br/>
        <strong>Impact Score:</strong> ${hovered.score} / 100 (${riskLvl})<br/>
        <strong>Status:</strong> ${a.is_compromised ? '⚠️ Compromised' : a.status}
      `;
    } else {
      tooltip.classList.add("hidden");
    }
  });

  canvas.addEventListener("mouseleave", () => {
    tooltip.classList.add("hidden");
  });
}


// ==============================================================
// 8. AI THREAT EXPLANATION CONTROLLER
// ==============================================================

function populateAiEventDropdown() {
  const select = document.getElementById("aiEventSelect");
  if (!select) return;

  select.innerHTML = "";

  // Add correlated incidents first
  allIncidents.forEach(inc => {
    const opt = document.createElement("option");
    opt.value = `inc:${inc.id}`;
    opt.textContent = `[CORRELATED INCIDENT] ${inc.title}`;
    select.appendChild(opt);
  });

  // Add individual security events
  allEvents.forEach(evt => {
    const opt = document.createElement("option");
    opt.value = `evt:${evt.id}`;
    opt.textContent = `[EVENT ${evt.id}] [${evt.severity}] ${evt.event_type} (${evt.source_asset_id})`;
    select.appendChild(opt);
  });

  // Automatically trigger first explanation
  if (select.options.length > 0) {
    handleAiEventSelection();
  }
}

async function handleAiEventSelection() {
  const select = document.getElementById("aiEventSelect");
  if (!select || !select.value) return;

  const val = select.value;
  const isIncident = val.startsWith("inc:");
  const id = val.replace("inc:", "").replace("evt:", "");

  setElText("aiAnswerWhatHappened", "Generating transparent explanation...");
  setElText("aiAnswerWhyDangerous", "Analyzing cyber-physical safety boundary impacts...");
  setElText("aiAnswerAffectedAsset", "Resolving affected controllers...");
  setElText("aiAnswerPropagation", "Tracing communication protocol path...");
  setElText("aiAnswerOperationalImpact", "Evaluating machinery impact...");
  setElText("aiAnswerInvestigation", "Formulating operator mitigation steps...");

  try {
    const reqBody = isIncident ? { incident_id: id } : { event_id: id };
    const res = await fetch("/api/ai/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reqBody)
    });

    if (!res.ok) return;
    const data = await res.json();

    // 1. Explainer Mode Banner
    const engineBadge = document.getElementById("aiActiveEngineBadge");
    if (engineBadge) engineBadge.textContent = data.explainer_mode;

    // 2. The 6 Explicit Questions
    setElText("aiAnswerWhatHappened", data.what_happened);
    setElText("aiAnswerWhyDangerous", data.why_dangerous || data.cyber_physical_risk);
    setElText("aiAnswerAffectedAsset", data.affected_asset || "Multiple connected controllers");
    setElText("aiAnswerPropagation", data.propagation_path || "Lateral network traversal across Purdue layers");
    setElText("aiAnswerOperationalImpact", data.operational_impact || data.cyber_physical_risk);
    
    const recBox = document.getElementById("aiAnswerInvestigation");
    if (recBox) {
      recBox.innerHTML = (data.investigation_steps || data.recommended_action).replace(/\n/g, "<br/>");
    }

    // 3. Technical Telemetry Context
    const techBox = document.getElementById("aiTechnicalBox");
    if (techBox) {
      techBox.textContent = JSON.stringify(data.technical_details, null, 2);
    }

  } catch (err) {
    console.error("AI explanation error:", err);
  }
}

function jumpToExplainEvent(eventId) {
  navigateToPage("dash-ai-explain");
  const select = document.getElementById("aiEventSelect");
  if (select) {
    select.value = `evt:${eventId}`;
    handleAiEventSelection();
  }
}


// ==============================================================
// 9. INCIDENT / EVENT CORRELATION CONTROLLER
// ==============================================================

async function loadCorrelations() {
  try {
    const res = await fetch("/api/correlations");
    if (!res.ok) return;
    allIncidents = await res.json();
    setElText("correlationCountBadge", `${allIncidents.length} Active Incident${allIncidents.length === 1 ? '' : 's'}`);
    renderCorrelationsList(allIncidents);
    renderCorrelationTimeline(allIncidents[0]);
  } catch (err) {
    console.error("Error loading correlations:", err);
  }
}

function renderCorrelationsList(incidents) {
  const container = document.getElementById("correlationListContainer");
  if (!container) return;

  container.innerHTML = "";
  if (incidents.length === 0) {
    container.innerHTML = `<div class="empty-state">No correlated incidents currently active. Baseline safe.</div>`;
    return;
  }

  incidents.forEach((inc, idx) => {
    const card = document.createElement("div");
    card.className = "incident-card";

    const tagsHtml = inc.involved_events.map(e => `<span class="incident-tag">${e}</span>`).join("");
    const assetsHtml = inc.involved_assets.map(a => `<span class="incident-tag text-cyan">${a}</span>`).join("");

    card.innerHTML = `
      <div class="incident-header">
        <div class="incident-title">${inc.title}</div>
        <span class="incident-time">${inc.timestamp}</span>
      </div>
      <p class="incident-desc">${inc.summary}</p>
      <div class="incident-tags">
        <span style="font-size: 0.7rem; color: var(--text-dim);">Events:</span> ${tagsHtml}
        <span style="font-size: 0.7rem; color: var(--text-dim); margin-left: 6px;">Assets:</span> ${assetsHtml}
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
        <button class="btn btn-sm btn-outline" onclick="renderCorrelationTimeline(allIncidents[${idx}])">
          View Sequence &rarr;
        </button>
        <button class="btn btn-sm btn-primary" onclick="jumpToExplainIncident('${inc.id}')">
          Explain Incident
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderCorrelationTimeline(incident) {
  const container = document.getElementById("correlationTimelineContainer");
  if (!container) return;

  if (!incident) {
    container.innerHTML = `<div class="empty-state">Select an incident to view attack chain sequence.</div>`;
    return;
  }

  const steps = [
    {
      time: "Step 1 &bull; Initial Ingress",
      title: "Off-Hours Perimeter Ingress (EVT-1001)",
      desc: "Unusual RDP connection flagged traversing perimeter firewall into Engineering Workstation subnet."
    },
    {
      time: "Step 2 &bull; Verification Violation",
      title: "Failed Operator Authentication Challenge (EVT-1002)",
      desc: "3 consecutive cryptographic challenge rejections at engineering console; unauthorized takeover suspected."
    },
    {
      time: "Step 3 &bull; OT Protocol Tampering",
      title: "Direct Modbus FC16 Write to Turbine Controller (EVT-1003)",
      desc: "Rogue Modbus command pushed directly to Gas Turbine PLC-01 speed governor registers."
    }
  ];

  container.innerHTML = `
    <h4 style="margin-bottom:14px; font-size:0.95rem; color:#fca5a5;">
      Sequence Chain: ${incident.title}
    </h4>
    <div class="sequence-timeline">
      ${steps.map(s => `
        <div class="timeline-step">
          <span class="timeline-dot"></span>
          <div style="font-size:0.75rem; color:var(--text-dim);">${s.time}</div>
          <strong style="font-size:0.85rem; display:block; margin:2px 0;">${s.title}</strong>
          <p style="font-size:0.78rem; color:var(--text-muted);">${s.desc}</p>
        </div>
      `).join("")}
    </div>
  `;
}

function jumpToExplainIncident(incidentId) {
  navigateToPage("dash-ai-explain");
  const select = document.getElementById("aiEventSelect");
  if (select) {
    select.value = `inc:${incidentId}`;
    handleAiEventSelection();
  }
}


// ==============================================================
// 10. ACCESS CONTROL / RBAC CONTROLLER
// ==============================================================

async function executeRBACCheck() {
  const role = document.querySelector('input[name="rbacRole"]:checked')?.value || (currentUser?.role || "operator");
  const action = document.getElementById("rbacActionSelect")?.value;
  const target = document.getElementById("rbacTargetSelect")?.value;
  const feedback = document.getElementById("rbacFeedbackBox");
  if (!feedback) return;

  try {
    const res = await fetch("/api/rbac/check-action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role: role,
        action: action,
        target_asset_id: target,
        operator_name: currentUser?.name || "Demo User"
      })
    });

    if (!res.ok) return;
    const data = await res.json();

    if (data.allowed) {
      feedback.className = "rbac-result-box result-success";
      feedback.innerHTML = `
        <strong>✓ ACTION AUTHORIZED:</strong><br/>
        Role '<strong>${data.role.toUpperCase()}</strong>' is permitted to execute '<code>${data.action}</code>' on <strong>${data.target_asset_id}</strong>.
      `;
    } else {
      feedback.className = "rbac-result-box result-denied";
      feedback.innerHTML = `
        <strong>⚠️ RBAC VIOLATION BLOCKED:</strong><br/>
        Role '<strong>${data.role.toUpperCase()}</strong>' is denied permission to perform '<code>${data.action}</code>'.<br/>
        <span style="font-size: 0.78rem;">Security Alert: An <strong>UNAUTHORIZED_ACCESS_ALERT</strong> was generated and logged into the active event stream!</span>
      `;
      // Refresh events and risk
      await loadRiskData();
      await loadEvents();
      await loadCorrelations();
    }
  } catch (err) {
    console.error("Error checking RBAC:", err);
  }
}


// ==============================================================
// 11. CRYPTOGRAPHIC INSPECTOR & SETTINGS
// ==============================================================

async function loadCryptoData() {
  try {
    const res = await fetch("/api/crypto/inspect");
    if (!res.ok) return;
    const data = await res.json();

    const credsContainer = document.getElementById("cryptoCredentialsContainer");
    if (credsContainer) {
      credsContainer.innerHTML = "";
      data.credentials_demo.forEach(c => {
        const item = document.createElement("div");
        item.className = "crypto-item";
        item.innerHTML = `
          <strong style="color: var(--accent-cyan);">${c.badge_id}</strong> (${c.role})<br/>
          <span style="color: var(--text-dim);">User:</span> ${c.operator_name}<br/>
          <span style="color: var(--text-dim);">Salt:</span> ${c.salt}<br/>
          <span style="color: var(--text-dim);">Stored SHA-256 Hash:</span><br/>
          <span style="word-break: break-all; color: #a7f3d0;">${c.stored_hash}</span>
        `;
        credsContainer.appendChild(item);
      });
    }

    setElText("cipherAlgo", data.encrypted_plc_config.cipher_algorithm);
    setElText("plaintextConfig", data.encrypted_plc_config.plaintext_preview);
    setElText("ciphertextDisplay", data.encrypted_plc_config.ciphertext);

  } catch (err) {
    console.error("Error loading crypto data:", err);
  }
}

async function resetSimulation() {
  if (!confirm("Reset all industrial assets, exposure paths, and simulation state to baseline?")) return;
  try {
    const res = await fetch("/api/reset", { method: "POST" });
    if (res.ok) {
      activeExposurePaths = [];
      await loadAllData();
      alert("IndustrialShield simulation reset to nominal baseline.");
    }
  } catch (err) {
    console.error("Error resetting simulation:", err);
  }
}
