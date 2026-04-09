from typing import List, Dict, Any
from datetime import datetime, timedelta
from ..database import SessionLocal, PrivacyLog

class LogService:
    @staticmethod
    def get_privacy_logs(limit: int = 50, agent_filter: str = None,
                        status_filter: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve privacy compliance logs"""
        db = SessionLocal()
        try:
            query = db.query(PrivacyLog)

            # Apply filters
            if agent_filter:
                query = query.filter(PrivacyLog.agent_name == agent_filter)

            if status_filter:
                query = query.filter(PrivacyLog.status == status_filter)

            # Date filter
            since_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(PrivacyLog.timestamp >= since_date)

            # Order by timestamp descending
            query = query.order_by(PrivacyLog.timestamp.desc())

            # Limit results
            logs = query.limit(limit).all()

            return [{
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "agent_name": log.agent_name,
                "data_accessed": log.data_accessed,
                "purpose": log.purpose,
                "status": log.status
            } for log in logs]

        finally:
            db.close()

    @staticmethod
    def get_log_summary(days: int = 7) -> Dict[str, Any]:
        """Get summary statistics for logs"""
        db = SessionLocal()
        try:
            since_date = datetime.utcnow() - timedelta(days=days)

            # Total logs
            total_logs = db.query(PrivacyLog).filter(
                PrivacyLog.timestamp >= since_date
            ).count()

            # Status breakdown
            status_counts = {}
            for status in ["Approved", "Review", "Blocked"]:
                count = db.query(PrivacyLog).filter(
                    PrivacyLog.timestamp >= since_date,
                    PrivacyLog.status == status
                ).count()
                status_counts[status] = count

            # Agent breakdown
            agent_counts = {}
            agents = ["Collection Agent", "Processing Agent", "Privacy Agent",
                     "Linking Agent", "Fraud Agent"]

            for agent in agents:
                count = db.query(PrivacyLog).filter(
                    PrivacyLog.timestamp >= since_date,
                    PrivacyLog.agent_name == agent
                ).count()
                agent_counts[agent] = count

            return {
                "total_logs": total_logs,
                "status_breakdown": status_counts,
                "agent_breakdown": agent_counts,
                "period_days": days
            }

        finally:
            db.close()

    @staticmethod
    def export_logs(format: str = "CSV", days: int = 30) -> str:
        """Export logs in specified format"""
        logs = LogService.get_privacy_logs(limit=1000, days=days)

        if format.upper() == "CSV":
            import csv
            import io

            output = io.StringIO()
            if logs:
                writer = csv.DictWriter(output, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)

            return output.getvalue()

        elif format.upper() == "JSON":
            import json
            return json.dumps(logs, indent=2)

        else:
            raise ValueError(f"Unsupported format: {format}")