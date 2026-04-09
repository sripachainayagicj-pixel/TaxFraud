from typing import Dict, Any, List
import pandas as pd
from .graph_service import GraphService

class FraudService:
    @staticmethod
    def calculate_risk_score(entity_data: Dict[str, Any], graph_data: Dict[str, Any] = None) -> float:
        """Calculate comprehensive risk score for an entity"""
        risk_score = 0

        # Financial risk factors
        import_amount = entity_data.get("import_amount", 0) or 0
        tax_paid = entity_data.get("tax_paid", 0) or 0

        # High imports with low tax
        if import_amount > 100000 and tax_paid < import_amount * 0.01:
            risk_score += 0.5

        # Zero tax on high imports
        if import_amount > 50000 and tax_paid == 0:
            risk_score += 0.3

        # Graph-based risk factors
        if graph_data:
            degree = graph_data.get("degree", 0)
            # High connectivity
            if degree > 5:
                risk_score += min(degree * 0.05, 0.3)

            # Connected to suspicious entities
            suspicious_connections = graph_data.get("suspicious_connections", 0)
            risk_score += suspicious_connections * 0.1

        return min(risk_score, 1.0)  # Cap at 1.0

    @staticmethod
    def detect_anomalies(entities_df: pd.DataFrame, transactions_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect various types of anomalies"""
        anomalies = []

        # Statistical anomalies in import amounts
        if not entities_df.empty and 'import_amount' in entities_df.columns:
            mean_import = entities_df['import_amount'].mean()
            std_import = entities_df['import_amount'].std()

            for _, entity in entities_df.iterrows():
                import_amt = entity.get('import_amount', 0)
                if import_amt > mean_import + 3 * std_import:
                    anomalies.append({
                        "entity_id": entity.get('company_id'),
                        "type": "statistical_outlier",
                        "description": f"Import amount {import_amt} is 3+ standard deviations above mean",
                        "severity": "medium"
                    })

        # Zero tax anomalies
        zero_tax_entities = entities_df[
            (entities_df['import_amount'] > 50000) &
            (entities_df['tax_paid'] == 0)
        ]

        for _, entity in zero_tax_entities.iterrows():
            anomalies.append({
                "entity_id": entity.get('company_id'),
                "type": "zero_tax_anomaly",
                "description": f"High imports (${entity['import_amount']}) with zero tax paid",
                "severity": "high"
            })

        # Circular transaction patterns
        if not transactions_df.empty:
            # Simple circular pattern detection
            transaction_pairs = transactions_df.groupby(['source', 'target']).size().reset_index(name='count')

            # Look for A->B and B->A patterns
            for _, row in transaction_pairs.iterrows():
                reverse = transaction_pairs[
                    (transaction_pairs['source'] == row['target']) &
                    (transaction_pairs['target'] == row['source'])
                ]

                if not reverse.empty:
                    anomalies.append({
                        "entity_id": f"{row['source']}-{row['target']}",
                        "type": "circular_transaction",
                        "description": f"Circular transactions between {row['source']} and {row['target']}",
                        "severity": "medium"
                    })

        return anomalies

    @staticmethod
    def generate_fraud_report(suspicious_entities: List[Dict[str, Any]],
                            graph_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive fraud report"""
        report = {
            "summary": {
                "total_suspicious_entities": len(suspicious_entities),
                "high_risk_count": len([e for e in suspicious_entities if e.get("risk_score", 0) > 0.7]),
                "total_clusters": len(graph_analysis.get("clusters", {})),
                "circular_patterns": len(graph_analysis.get("cycles", []))
            },
            "risk_distribution": {
                "low": len([e for e in suspicious_entities if e.get("risk_score", 0) <= 0.3]),
                "medium": len([e for e in suspicious_entities if 0.3 < e.get("risk_score", 0) <= 0.7]),
                "high": len([e for e in suspicious_entities if e.get("risk_score", 0) > 0.7])
            },
            "top_suspicious_entities": sorted(
                suspicious_entities,
                key=lambda x: x.get("risk_score", 0),
                reverse=True
            )[:10]
        }

        return report