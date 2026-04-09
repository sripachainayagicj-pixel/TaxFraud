from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db, HighRiskEntity
from ..models import DashboardData, HighRiskEntity as HighRiskEntityModel
from ..services.log_service import LogService

router = APIRouter()

@router.get("/dashboard", response_model=DashboardData)
def get_dashboard_data(db: Session = Depends(get_db)):
    """Get dashboard metrics and high-risk entities"""
    try:
        # Get high-risk entities
        high_risk_entities = db.query(HighRiskEntity).all()

        # Convert to response format
        entities_list = []
        for entity in high_risk_entities:
            entities_list.append({
                "company_id": entity.company_id,
                "reason": entity.reason,
                "import_value": entity.import_value,
                "tax_paid": entity.tax_paid,
                "risk_score": entity.risk_score
            })

        # Mock some metrics (in a real app, these would be calculated)
        # For now, base them on the high-risk entities
        records_scanned = 3473  # Mock value
        cross_agency_links = 4245  # Mock value
        anomalies_detected = len(high_risk_entities)

        return DashboardData(
            records_scanned=records_scanned,
            cross_agency_links=cross_agency_links,
            anomalies_detected=anomalies_detected,
            high_risk_entities=entities_list
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

@router.get("/high-risk", response_model=List[HighRiskEntityModel])
def get_high_risk_entities(db: Session = Depends(get_db)):
    """Get all high-risk entities"""
    try:
        entities = db.query(HighRiskEntity).all()

        return [{
            "company_id": entity.company_id,
            "reason": entity.reason,
            "import_value": entity.import_value,
            "tax_paid": entity.tax_paid,
            "risk_score": entity.risk_score
        } for entity in entities]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching high-risk entities: {str(e)}")