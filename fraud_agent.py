import pandas as pd
import networkx as nx
from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..database import SessionLocal, HighRiskEntity

class FraudDetectionAgent(BaseAgent):
    def __init__(self, risk_threshold: float = 0.7):
        super().__init__("Fraud Agent")
        self.risk_threshold = risk_threshold

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect suspicious entities using graph analytics"""
        self.update_status(status="running")

        try:
            business_df = data.get("business", pd.DataFrame())
            edges = data.get("edges", [])

            # Build NetworkX graph
            G = nx.Graph()

            # Add nodes with attributes
            for _, row in business_df.iterrows():
                cid = row.get("company_id")
                if pd.notna(cid):
                    G.add_node(cid, **row.to_dict())

            # Add edges
            for edge in edges:
                G.add_edge(
                    edge["source"],
                    edge["target"],
                    type=edge["type"],
                    weight=edge.get("value", 1)
                )

            # Analyze for fraud patterns
            suspicious_companies = []
            import_threshold = 100000

            for node, node_attr in G.nodes(data=True):
                risk_score = 0
                reasons = []

                import_amt = node_attr.get("import_amount", 0)
                if pd.isna(import_amt):
                    import_amt = 0
                tax_paid = node_attr.get("tax_paid", 0)
                if pd.isna(tax_paid):
                    tax_paid = 0

                # High imports with low/no tax
                if import_amt > import_threshold and tax_paid <= 500:
                    risk_score += 50
                    reasons.append("High imports with zero/low tax")

                # High connectivity (potential circular trading)
                degree = G.degree[node] if node in G else 0
                if degree > 3:
                    risk_score += 20 * min(degree, 5)  # Cap at 5 for scoring
                    reasons.append(f"Highly connected entity (degree {degree})")

                # Connected to other suspicious entities
                suspicious_neighbors = 0
                for neighbor in G.neighbors(node):
                    neighbor_attr = G.nodes[neighbor]
                    n_import = neighbor_attr.get("import_amount", 0)
                    n_tax = neighbor_attr.get("tax_paid", 0)
                    if n_import > import_threshold and n_tax <= 500:
                        suspicious_neighbors += 1

                if suspicious_neighbors > 0:
                    risk_score += 15 * suspicious_neighbors
                    reasons.append(f"Connected to {suspicious_neighbors} suspicious entities")

                # Flag if risk score is high enough
                if risk_score >= self.risk_threshold * 100:
                    suspicious_companies.append({
                        "company_id": node,
                        "reason": " + ".join(reasons),
                        "import_amount": import_amt,
                        "tax_paid": tax_paid,
                        "risk_score": risk_score / 100.0  # Normalize to 0-1
                    })

            # Store suspicious companies in database
            db = SessionLocal()
            try:
                # Clear previous results
                db.query(HighRiskEntity).delete()

                for company in suspicious_companies:
                    db_entity = HighRiskEntity(
                        company_id=company["company_id"],
                        reason=company["reason"],
                        import_value=company["import_amount"],
                        tax_paid=company["tax_paid"],
                        risk_score=company["risk_score"]
                    )
                    db.add(db_entity)
                db.commit()
            finally:
                db.close()

            # Prepare graph data for frontend
            ui_nodes = []
            ui_links = []

            for node in G.nodes():
                # Determine group (1 for companies, 2 for others - but all are companies here)
                is_suspicious = any(s["company_id"] == node for s in suspicious_companies)
                ui_nodes.append({
                    "id": node,
                    "group": 1,  # All are companies
                    "risk": next((s["risk_score"] for s in suspicious_companies if s["company_id"] == node), 0)
                })

            for u, v, edge_data in G.edges(data=True):
                ui_links.append({
                    "source": u,
                    "target": v,
                    "type": edge_data.get("type", "transaction"),
                    "value": edge_data.get("weight", 1)
                })

            # Log privacy action
            self.log_privacy_action(
                data_accessed="Graph analytics and fraud patterns",
                purpose="Fraud detection and risk scoring",
                status="Approved"
            )

            self.update_status(records_processed=len(suspicious_companies), status="completed")

            return {
                "suspicious_companies": suspicious_companies,
                "graph": {
                    "nodes": ui_nodes,
                    "links": ui_links
                },
                "anomalies_detected": len(suspicious_companies),
                "total_nodes": len(ui_nodes),
                "total_links": len(ui_links)
            }

        except Exception as e:
            self.update_status(status="error")
            raise e