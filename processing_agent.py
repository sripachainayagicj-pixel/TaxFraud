import pandas as pd
from typing import Dict, Any
from .base_agent import BaseAgent

class ProcessingAgent(BaseAgent):
    def __init__(self):
        super().__init__("Processing Agent")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize transaction data"""
        self.update_status(status="running")

        try:
            business_df = data.get("business", pd.DataFrame())
            transactions_df = data.get("transactions", pd.DataFrame())

            # Clean business data
            if not business_df.empty:
                # Fill missing values
                business_df = business_df.fillna({
                    'import_amount': 0,
                    'tax_paid': 0,
                    'owner': 'Unknown',
                    'director': 'Unknown',
                    'address': 'Unknown',
                    'tax_id': 'Unknown'
                })

                # Ensure numeric columns are numeric
                business_df['import_amount'] = pd.to_numeric(business_df['import_amount'], errors='coerce').fillna(0)
                business_df['tax_paid'] = pd.to_numeric(business_df['tax_paid'], errors='coerce').fillna(0)

            # Clean transaction data
            if not transactions_df.empty:
                transactions_df['amount'] = pd.to_numeric(transactions_df['amount'], errors='coerce').fillna(0)

                # Remove invalid transactions
                transactions_df = transactions_df[
                    (transactions_df['amount'] > 0) &
                    (transactions_df['source'].notna()) &
                    (transactions_df['target'].notna())
                ]

            # Log privacy action
            self.log_privacy_action(
                data_accessed="Raw transaction and business data",
                purpose="Data cleaning and normalization",
                status="Approved"
            )

            records_processed = len(business_df) + len(transactions_df)
            self.update_status(records_processed=records_processed, status="completed")

            return {
                "business": business_df,
                "transactions": transactions_df,
                "processed_records": records_processed
            }

        except Exception as e:
            self.update_status(status="error")
            raise e