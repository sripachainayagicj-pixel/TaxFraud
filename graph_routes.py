from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db, HighRiskEntity
from ..models import GraphData

router = APIRouter()

@router.get("/graph", response_model=GraphData)
def get_graph_data(db: Session = Depends(get_db)):
    """Get graph data for visualization"""
    try:
        # Get high-risk entities to determine node groups
        high_risk_entities = db.query(HighRiskEntity).all()
        suspicious_ids = {entity.company_id for entity in high_risk_entities}

        # Mock graph data (in a real app, this would be stored in database)
        # For demo purposes, create a sample graph
        nodes = []
        links = []

        # Create nodes for companies C1-C40
        for i in range(1, 41):
            company_id = f"C{i}"
            is_suspicious = company_id in suspicious_ids
            risk_score = 0.85 if company_id == "C36" else 0.0  # C36 is our main suspicious entity

            nodes.append({
                "id": company_id,
                "group": 1,  # All are companies
                "risk": risk_score
            })

        # Create links based on relationships
        # Transaction links
        transactions = [
            ("C1", "C2"), ("C2", "C3"), ("C3", "C4"), ("C4", "C5"),
            ("C5", "C6"), ("C6", "C7"), ("C7", "C8"), ("C8", "C9"),
            ("C9", "C10"), ("C10", "C11"), ("C11", "C12"), ("C12", "C13"),
            ("C13", "C14"), ("C14", "C15"), ("C15", "C16"), ("C16", "C17"),
            ("C17", "C18"), ("C18", "C19"), ("C19", "C20"), ("C20", "C21"),
            ("C21", "C22"), ("C22", "C23"), ("C23", "C24"), ("C24", "C25"),
            ("C25", "C26"), ("C26", "C27"), ("C27", "C28"), ("C28", "C29"),
            ("C29", "C30"), ("C30", "C31"), ("C31", "C32"), ("C32", "C33"),
            ("C33", "C34"), ("C34", "C35"), ("C35", "C36"),
            ("C36", "C1"), ("C36", "C2"), ("C36", "C3")  # Circular transactions
        ]

        for source, target in transactions:
            links.append({
                "source": source,
                "target": target,
                "type": "transaction",
                "value": 1
            })

        # Add some shared relationship links
        shared_relationships = [
            ("C1", "C5", "shared_director"),
            ("C2", "C7", "shared_address"),
            ("C3", "C8", "shared_tax_id"),
            ("C10", "C15", "shared_director"),
            ("C20", "C25", "shared_address")
        ]

        for source, target, rel_type in shared_relationships:
            links.append({
                "source": source,
                "target": target,
                "type": rel_type,
                "value": 1
            })

        return GraphData(nodes=nodes, links=links)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching graph data: {str(e)}")