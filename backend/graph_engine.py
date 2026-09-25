from typing import List, Dict, Any, Optional, Tuple
import networkx as nx
from .models import ImpactAnalysisResponse
from .assets import asset_manager


class IndustrialGraphEngine:
    """
    NetworkX-based industrial topology and impact analysis engine.
    Models Purdue Model network hierarchy and calculates exposure paths and blast radii.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_topology()

    def _build_topology(self):
        """Constructs the directed industrial communication network based on ISA-95 / Purdue Model."""
        self.graph.clear()

        # Add nodes with metadata
        for asset in asset_manager.get_all_assets():
            self.graph.add_node(
                asset.id,
                name=asset.name,
                stage=asset.stage.value,
                criticality=asset.criticality,
                protocol=asset.protocol,
                ip=asset.ip_address
            )

        # Industrial Communication Links (Directed Edges):
        # Level 4 to Level 3.5 (Enterprise to DMZ)
        self.graph.add_edge("CORP-ERP", "DMZ-FIREWALL", protocol="HTTPS/TLS", port=443, description="Production scheduling API")
        self.graph.add_edge("DMZ-FIREWALL", "DMZ-HISTORIAN-MIRROR", protocol="OPC UA Forwarding", port=4840, description="DMZ data relay")

        # Level 3.5 to Level 3 (DMZ to Operations)
        self.graph.add_edge("DMZ-HISTORIAN-MIRROR", "PLANT-HISTORIAN", protocol="OPC UA / Sync", port=4840, description="Mirror replication pipe")
        self.graph.add_edge("DMZ-FIREWALL", "ENG-WORKSTATION-01", protocol="RDP / VPN Jump", port=3389, description="Remote vendor support tunnel (High Risk)")

        # Level 3 Operations interconnections
        self.graph.add_edge("PLANT-HISTORIAN", "SCADA-SERVER-01", protocol="TCP/IP", port=1433, description="Process telemetry pipeline")
        self.graph.add_edge("ENG-WORKSTATION-01", "SCADA-SERVER-01", protocol="Proprietary Remote Admin", port=502, description="SCADA project deployment")
        self.graph.add_edge("ENG-WORKSTATION-01", "PLC-TURBINE-01", protocol="S7comm / Modbus Engineering", port=102, description="Direct ladder logic upload pipe")
        self.graph.add_edge("ENG-WORKSTATION-01", "SIS-01", protocol="Safety Engineering Tool", port=44818, description="Safety logic configuration port (Airgap violation risk)")

        # Level 3 to Level 2 (Operations to Supervisory HMIs)
        self.graph.add_edge("SCADA-SERVER-01", "HMI-TURBINE", protocol="Modbus TCP", port=502, description="Supervisory tag polling")
        self.graph.add_edge("SCADA-SERVER-01", "HMI-COOLING", protocol="EtherNet/IP", port=44818, description="Chiller supervisory tags")

        # Level 2 to Level 1 (HMIs to Real-Time PLCs)
        self.graph.add_edge("HMI-TURBINE", "PLC-TURBINE-01", protocol="Modbus TCP", port=502, description="Setpoint adjustments & start/stop commands")
        self.graph.add_edge("HMI-COOLING", "PLC-COOLING-02", protocol="Modbus TCP", port=502, description="Pump speed & fan regulation")

        # Level 1 to Level 0 (PLCs & SIS to Physical Actuators and Sensors)
        self.graph.add_edge("PLC-TURBINE-01", "VALVE-PRESSURE-01", protocol="HART / 4-20mA", port=0, description="Steam dump solenoid trigger")
        self.graph.add_edge("PLC-TURBINE-01", "TEMP-SENSOR-01", protocol="Modbus RTU", port=0, description="Combustion thermal polling")
        self.graph.add_edge("PLC-COOLING-02", "PUMP-COOLING-01", protocol="Digital Relay Output", port=0, description="Motor contactor energization")

        # Autonomous Safety Link (SIS connects directly to emergency actuator)
        self.graph.add_edge("SIS-01", "VALVE-PRESSURE-01", protocol="Hardwired Safety Relays (SIL-3)", port=0, description="Autonomous fail-safe dump line")

    def get_topology_data(self) -> Dict[str, Any]:
        """Returns node and edge definitions formatted for frontend visual rendering."""
        # Refresh dynamic asset status
        nodes = []
        for n, data in self.graph.nodes(data=True):
            asset = asset_manager.get_asset(n)
            nodes.append({
                "id": n,
                "label": data.get("name", n),
                "stage": data.get("stage", ""),
                "criticality": data.get("criticality", 1),
                "protocol": data.get("protocol", ""),
                "ip": data.get("ip", ""),
                "status": asset.status.value if asset else "ONLINE",
                "is_compromised": asset.is_compromised if asset else False,
                "risk_score": asset.risk_score if asset else 0.0
            })

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "protocol": data.get("protocol", ""),
                "port": data.get("port", 0),
                "description": data.get("description", "")
            })

        # Calculate network centrality to detect chokepoint bridges
        centrality = nx.betweenness_centrality(self.graph)
        top_chokepoints = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "chokepoints": [{"asset_id": k, "centrality_score": round(v, 3)} for k, v in top_chokepoints]
        }

    def analyze_impact(self, source_node: str, target_node: Optional[str] = None) -> ImpactAnalysisResponse:
        """
        Uses NetworkX graph algorithms to:
        1. Discover potential attack exposure paths from the source to high-value assets or specified target.
        2. Calculate blast radius (all downstream reachable nodes).
        3. Identify critical safety assets in the exposure path.
        4. Recommend actionable industrial mitigations.
        """
        if source_node not in self.graph:
            return ImpactAnalysisResponse(
                source_node=source_node,
                target_node=target_node,
                exposure_paths=[],
                blast_radius_nodes=[],
                critical_assets_at_risk=[],
                exposure_risk_score=0.0,
                blast_radius_count=0,
                mitigation_steps=["Asset not found in Purdue topology graph."]
            )

        # Calculate blast radius using NetworkX descendants
        blast_radius = list(nx.descendants(self.graph, source_node))
        
        # Check critical safety assets at risk (criticality >= 4)
        critical_assets = []
        for node_id in blast_radius:
            asset = asset_manager.get_asset(node_id)
            if asset and asset.criticality >= 4:
                critical_assets.append(f"{node_id} ({asset.name})")

        # Discover exposure paths
        exposure_paths = []
        if target_node and target_node in self.graph:
            try:
                # Find all simple paths up to cutoff 6
                paths = list(nx.all_simple_paths(self.graph, source=source_node, target=target_node, cutoff=6))
                exposure_paths = paths[:5]  # limit to top 5
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                exposure_paths = []
        else:
            # Default: find exposure paths to the most critical controllers and actuators
            high_value_targets = ["SIS-01", "PLC-TURBINE-01", "VALVE-PRESSURE-01"]
            for hvt in high_value_targets:
                if hvt != source_node and nx.has_path(self.graph, source_node, hvt):
                    try:
                        shortest_p = nx.shortest_path(self.graph, source=source_node, target=hvt)
                        exposure_paths.append(shortest_p)
                    except nx.NetworkXNoPath:
                        continue

        # Calculate exposure score
        source_asset = asset_manager.get_asset(source_node)
        source_crit = source_asset.criticality if source_asset else 2
        reach_safety = any("SIS-01" in path for path in exposure_paths) or any("VALVE-PRESSURE-01" in path for path in exposure_paths)
        
        base_risk = 30.0 + (len(blast_radius) * 7.5) + (source_crit * 5.0)
        if reach_safety:
            base_risk += 35.0
        exposure_risk_score = min(100.0, round(base_risk, 1))

        # Generate targeted mitigation steps
        mitigation_steps = [
            f"Immediately activate network ACL rule to isolate {source_node} from Level 1/2 control subnet.",
            "Verify ladder logic hash on downstream PLCs to confirm no unapproved code modifications were written.",
            "Review firewall sessions traversing Level 3.5 DMZ and inspect OPC UA / Modbus port traffic.",
            "Enforce two-person verification for any remote engineering workstation connections."
        ]

        if reach_safety:
            mitigation_steps.insert(0, "CRITICAL WARNING: Exposure path touches Safety Instrumented System (SIS-01). Verify physical key switch is in RUN (not REMOTE PROGRAM) mode.")

        return ImpactAnalysisResponse(
            source_node=source_node,
            target_node=target_node,
            exposure_paths=exposure_paths,
            blast_radius_nodes=blast_radius,
            critical_assets_at_risk=critical_assets,
            exposure_risk_score=exposure_risk_score,
            blast_radius_count=len(blast_radius),
            mitigation_steps=mitigation_steps
        )


# Singleton instance
graph_engine = IndustrialGraphEngine()
