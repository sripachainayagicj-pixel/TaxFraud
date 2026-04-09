import pandas as pd
from typing import Dict
from .base_agent import BaseAgent

class DataProcessingAgent(BaseAgent):
    def run(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        processed = {}
        for name, df in datasets.items():
            processed_df = df.copy()
            if "company_id" in processed_df.columns:
                processed_df["company_id"] = processed_df["company_id"].astype(str).str.strip().str.upper()
            if "owner" in processed_df.columns:
                processed_df["owner"] = processed_df["owner"].astype(str).str.strip().str.title()
            if "director" in processed_df.columns:
                processed_df["director"] = processed_df["director"].astype(str).str.strip().str.title()
            if "address" in processed_df.columns:
                processed_df["address"] = processed_df["address"].astype(str).str.strip().str.lower()
            processed[name] = processed_df
        return processed
