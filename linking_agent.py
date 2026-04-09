import pandas as pd
import networkx as nx
from typing import Dict, Any, List
from .base_agent import BaseAgent

class LinkingAgent(BaseAgent):
    def __init__(self, key_col: str = "company_id"):
        super().__init__("Linking Agent")
        self.key_col = key_col

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build graph relationships and create edges"""
        self.update_status(status="running")

        try:
            business_df = data.get("business", pd.DataFrame())
            transactions_df = data.get("transactions", pd.DataFrame())

            edges = []

            # Create transaction edges
            if not transactions_df.empty:
                for _, row in transactions_df.iterrows():
                    source = row.get("source")
                    target = row.get("target")
                    amount = row.get("amount", 0)
                    if pd.notna(source) and pd.notna(target):
                        edges.append({
                            "source": source,
                            "target": target,
                            "type": "transaction",
                            "value": amount
                        })

            # Create relationship edges based on shared attributes
            if not business_df.empty:
                # Shared directors
                dir_to_companies = {}
                for _, row in business_df.iterrows():
                    cid = row.get(self.key_col)
                    director = row.get("director")
                    if pd.notna(director) and director != "Unknown":
                        dir_to_companies.setdefault(director, []).append(cid)

                for director, companies in dir_to_companies.items():
                    if len(companies) > 1:
                        for i in range(len(companies)):
                            for j in range(i + 1, len(companies)):
                                edges.append({
                                    "source": companies[i],
                                    "target": companies[j],
                                    "type": "shared_director",
                                    "value": 1
                                })

                # Shared addresses
                addr_to_companies = {}
                for _, row in business_df.iterrows():
                    cid = row.get(self.key_col)
                    address = row.get("address")
                    if pd.notna(address) and address != "Unknown":
                        addr_to_companies.setdefault(address, []).append(cid)

                for address, companies in addr_to_companies.items():
                    if len(companies) > 1:
                        for i in range(len(companies)):
                            for j in range(i + 1, len(companies)):
                                edges.append({
                                    "source": companies[i],
                                    "target": companies[j],
                                    "type": "shared_address",
                                    "value": 1
                                })

                # Shared tax IDs
                tax_to_companies = {}
                for _, row in business_df.iterrows():
                    cid = row.get(self.key_col)
                    tax_id = row.get("tax_id")
                    if pd.notna(tax_id) and tax_id != "Unknown":
                        tax_to_companies.setdefault(tax_id, []).append(cid)

                for tax_id, companies in tax_to_companies.items():
                    if len(companies) > 1:
                        for i in range(len(companies)):
                            for j in range(i + 1, len(companies)):
                                edges.append({
                                    "source": companies[i],
                                    "target": companies[j],
                                    "type": "shared_tax_id",
                                    "value": 1
                                })

            # Log privacy action
            self.log_privacy_action(
                data_accessed="Entity relationship data",
                purpose="Graph construction for fraud analysis",
                status="Approved"
            )

            self.update_status(records_processed=len(edges), status="completed")

            return {
                "business": business_df,
                "transactions": transactions_df,
                "edges": edges,
                "link_count": len(edges)
            }

        except Exception as e:
            self.update_status(status="error")
            raise e