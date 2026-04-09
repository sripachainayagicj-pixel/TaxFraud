from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database import get_db, AgentStatus
from ..models import AgentStatus as AgentStatusModel

router = APIRouter()

@router.get("/agents-status")
def get_agents_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get status of all agents"""
    try:
        agents = db.query(AgentStatus).all()

        # Create a dict of agent statuses
        status_dict = {}
        agent_names = ["Collection Agent", "Processing Agent", "Privacy Agent",
                      "Linking Agent", "Fraud Agent"]

        for agent_name in agent_names:
            agent = next((a for a in agents if a.agent_name == agent_name), None)
            if agent:
                status_dict[agent_name.lower().replace(" ", "_")] = {
                    "last_run": agent.last_run.strftime("%I:%M %p") if agent.last_run else None,
                    "records_processed": agent.records_processed,
                    "status": agent.status
                }
            else:
                # Default status for agents that haven't run
                status_dict[agent_name.lower().replace(" ", "_")] = {
                    "last_run": None,
                    "records_processed": 0,
                    "status": "idle"
                }

        return status_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent status: {str(e)}")

@router.get("/agents/{agent_name}/status", response_model=AgentStatusModel)
def get_agent_status(agent_name: str, db: Session = Depends(get_db)):
    """Get status of a specific agent"""
    try:
        agent = db.query(AgentStatus).filter(AgentStatus.agent_name == agent_name).first()

        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")

        return AgentStatusModel(
            agent_name=agent.agent_name,
            last_run=agent.last_run,
            records_processed=agent.records_processed,
            status=agent.status
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent status: {str(e)}")