import json
import pandas as pd
from typing import Dict, Any
from .base_agent import BaseAgent

class CollectionAgent(BaseAgent):
    def __init__(self, dataset_path: str = "backend/data/demo_dataset.json"):
        super().__init__("Collection Agent")
        self.dataset_path = dataset_path

    def run(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Load and collect data from various sources"""
        self.update_status(status="running")

        try:
            # Load demo dataset
            with open(self.dataset_path, 'r') as f:
                dataset = json.load(f)

            # Convert to DataFrames
            business_df = pd.DataFrame(dataset.get("business", []))
            transactions_df = pd.DataFrame(dataset.get("transactions", []))

            # Log privacy action
            self.log_privacy_action(
                data_accessed="Business registry and transaction records",
                purpose="Data ingestion for fraud analysis",
                status="Approved"
            )

            records_count = len(business_df) + len(transactions_df)
            self.update_status(records_processed=records_count, status="completed")

            return {
                "business": business_df,
                "transactions": transactions_df,
                "records_count": records_count
            }

        except Exception as e:
            self.update_status(status="error")
            raise e