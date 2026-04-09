import pandas as pd
from typing import Dict
from .base_agent import BaseAgent

class DataLinkingAgent(BaseAgent):
    def __init__(self, key_col: str):
        self.key_col = key_col

    def run(self, datasets: Dict[str, pd.DataFrame]) -> dict:
        if "business" not in datasets:
            return {"entities": pd.DataFrame(), "transactions": pd.DataFrame(), "edges": []}
        
        business_df = datasets["business"]
        entities = business_df.copy()
        if "tax" in datasets:
            entities = entities.merge(datasets["tax"], on=self.key_col, how="left")
        if "customs" in datasets:
            entities = entities.merge(datasets["customs"], on=self.key_col, how="left")
            
        transactions = datasets.get("transactions", pd.DataFrame())
        
        edges = []
        if not transactions.empty:
            for _, row in transactions.iterrows():
                src = row.get("source")
                tgt = row.get("target")
                amt = row.get("amount", 0)
                if pd.notna(src) and pd.notna(tgt):
                    edges.append({"source": src, "target": tgt, "type": "transaction", "value": amt})
        
        if not business_df.empty:
            dir_to_companies = {}
            addr_to_companies = {}
            tax_to_companies = {}
            for _, row in business_df.iterrows():
                cid = row.get("company_id")
                d = row.get("director")
                a = row.get("address")
                t = row.get("tax_id")
                if pd.notna(d) and d != "nan" and d.strip() != "":
                    dir_to_companies.setdefault(d, []).append(cid)
                if pd.notna(a) and a != "nan" and a.strip() != "":
                    addr_to_companies.setdefault(a, []).append(cid)
                if pd.notna(t) and t != "nan" and t.strip() != "":
                    tax_to_companies.setdefault(t, []).append(cid)
                    
            for d, cids in dir_to_companies.items():
                if len(cids) > 1:
                    for i in range(len(cids)):
                        for j in range(i+1, len(cids)):
                            edges.append({"source": cids[i], "target": cids[j], "type": "shared_director", "value": 1})
                            
            for a, cids in addr_to_companies.items():
                if len(cids) > 1:
                    for i in range(len(cids)):
                        for j in range(i+1, len(cids)):
                            edges.append({"source": cids[i], "target": cids[j], "type": "shared_address", "value": 1})
                            
            for t, cids in tax_to_companies.items():
                if len(cids) > 1:
                    for i in range(len(cids)):
                        for j in range(i+1, len(cids)):
                            edges.append({"source": cids[i], "target": cids[j], "type": "shared_tax_id", "value": 1})
                            
        return {
            "entities": entities,
            "transactions": transactions,
            "edges": edges
        }
