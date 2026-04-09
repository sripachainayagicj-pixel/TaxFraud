import hashlib
import pandas as pd
from typing import Dict
from .base_agent import BaseAgent

class PrivacyAgent(BaseAgent):
    def __init__(self, sensitive_columns: Dict[str, list]):
        # e.g. {"business": ["owner"]}
        self.sensitive_columns = sensitive_columns

    def anonymize(self, val):
        if pd.isna(val) or val == "" or str(val).lower() == "nan":
            return val
        return hashlib.sha256(str(val).encode()).hexdigest()[:16]

    def run(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        anonymized = {}
        for name, df in datasets.items():
            output_df = df.copy()
            if name in self.sensitive_columns:
                for col in self.sensitive_columns[name]:
                    if col in output_df.columns:
                        output_df[col] = output_df[col].apply(self.anonymize)
            anonymized[name] = output_df
        return anonymized
