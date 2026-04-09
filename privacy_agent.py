import pandas as pd
import hashlib
from typing import Dict, Any, List
from .base_agent import BaseAgent

class PrivacyAgent(BaseAgent):
    def __init__(self, sensitive_fields: List[str] = None):
        super().__init__("Privacy Agent")
        self.sensitive_fields = sensitive_fields or ["owner", "director", "address", "tax_id"]

    def hash_value(self, value: str) -> str:
        """Create a consistent hash for anonymization"""
        if pd.isna(value) or value == "Unknown":
            return value
        return hashlib.sha256(str(value).encode()).hexdigest()[:16]

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive information"""
        self.update_status(status="running")

        try:
            business_df = data.get("business", pd.DataFrame()).copy()
            transactions_df = data.get("transactions", pd.DataFrame()).copy()

            # Anonymize sensitive fields in business data
            if not business_df.empty:
                for field in self.sensitive_fields:
                    if field in business_df.columns:
                        business_df[field] = business_df[field].apply(self.hash_value)

                        # Log each field anonymization
                        self.log_privacy_action(
                            data_accessed=f"Business {field} field",
                            purpose="PII anonymization",
                            status="Approved"
                        )

            # Transactions don't contain PII, but log access
            if not transactions_df.empty:
                self.log_privacy_action(
                    data_accessed="Transaction records",
                    purpose="PII masking verification",
                    status="Approved"
                )

            records_processed = len(business_df) + len(transactions_df)
            self.update_status(records_processed=records_processed, status="completed")

            return {
                "business": business_df,
                "transactions": transactions_df,
                "anonymized_records": records_processed
            }

        except Exception as e:
            self.update_status(status="error")
            raise e