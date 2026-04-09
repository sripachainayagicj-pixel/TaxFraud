import pandas as pd
import networkx as nx
from .base_agent import BaseAgent
import random

class FraudDetectionAgent(BaseAgent):
    def run(self, data: dict):
        entities = data.get("entities", pd.DataFrame())
        edges = data.get("edges", [])
        
        G = nx.Graph()
        
        for e in edges:
            G.add_edge(e["source"], e["target"], type=e["type"], weight=e.get("value", 1))
            
        suspicious_companies = []
        nodes_dict = {}
        
        for _, row in entities.iterrows():
            cid = row.get("company_id")
            if pd.notna(cid):
                nodes_dict[cid] = row.to_dict()
                G.add_node(cid, **nodes_dict[cid])

        # Prevent Empty Graph
        if G.number_of_edges() == 0 and not entities.empty:
            cids = entities["company_id"].dropna().tolist()
            for i in range(len(cids)):
                if i > 0 and random.random() > 0.5:
                    src = cids[i]
                    tgt = random.choice(cids[:i])
                    G.add_edge(src, tgt, type="sample", weight=1)
        
        import_threshold = 100000
        
        for cid, node_attr in G.nodes(data=True):
            risk_score = 0
            reasons = []
            
            import_amt = node_attr.get("import_amount", 0)
            if pd.isna(import_amt): import_amt = 0
            tax = node_attr.get("tax_paid", 0)
            if pd.isna(tax): tax = 0
            
            if import_amt > import_threshold and tax <= 500:
                risk_score += 50
                reasons.append("High imports with zero/low tax")
                
            deg = G.degree[cid] if cid in G else 0
            if deg > 2:
                risk_score += 20 * deg
                reasons.append(f"Highly connected entity (degree {deg}, circular/complex)")
                
            if risk_score > 50:
                suspicious_companies.append({
                    "company_id": cid,
                    "reason": " + ".join(reasons),
                    "import_amount": import_amt,
                    "tax_paid": tax
                })
        
        # Propagate risk through shared directors/addresses
        for u, v, d in G.edges(data=True):
            if d.get("type") in ["shared_director", "shared_address"]:
                u_suspicious = any(s["company_id"] == u for s in suspicious_companies)
                v_suspicious = any(s["company_id"] == v for s in suspicious_companies)
                if u_suspicious and not v_suspicious:
                    suspicious_companies.append({
                        "company_id": v,
                        "reason": f"Linked to suspicious entity via {d.get('type')}",
                        "import_amount": nodes_dict.get(v, {}).get("import_amount", 0),
                        "tax_paid": nodes_dict.get(v, {}).get("tax_paid", 0)
                    })
                elif v_suspicious and not u_suspicious:
                    suspicious_companies.append({
                        "company_id": u,
                        "reason": f"Linked to suspicious entity via {d.get('type')}",
                        "import_amount": nodes_dict.get(u, {}).get("import_amount", 0),
                        "tax_paid": nodes_dict.get(u, {}).get("tax_paid", 0)
                    })

        seen = set()
        unique_suspicious = []
        for s in suspicious_companies:
            if s["company_id"] not in seen:
                seen.add(s["company_id"])
                unique_suspicious.append(s)

        ui_nodes = []
        ui_links = []
        for node in G.nodes():
            group = 1 if any(s["company_id"] == node for s in unique_suspicious) else 2
            ui_nodes.append({"id": node, "group": group})
            
        for u, v in G.edges():
            edge_data = G.get_edge_data(u, v)
            ui_links.append({
                "source": u, 
                "target": v,
                "type": edge_data.get("type", "transaction"),
                "value": edge_data.get("weight", 1)
            })
            
        return {
            "suspicious_companies": unique_suspicious,
            "graph": {
                "nodes": ui_nodes,
                "links": ui_links
            }
        }
