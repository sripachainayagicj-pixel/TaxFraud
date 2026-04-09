from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from ..models import PrivacyLog
from ..services.log_service import LogService

router = APIRouter()

@router.get("/privacy-logs", response_model=List[PrivacyLog])
def get_privacy_logs(
    limit: int = Query(50, description="Maximum number of logs to return"),
    agent_filter: Optional[str] = Query(None, description="Filter by agent name"),
    status_filter: Optional[str] = Query(None, description="Filter by status (Approved/Review/Blocked)"),
    days: int = Query(7, description="Number of days to look back")
):
    """Get privacy compliance audit logs"""
    try:
        logs = LogService.get_privacy_logs(
            limit=limit,
            agent_filter=agent_filter,
            status_filter=status_filter,
            days=days
        )
        return logs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching privacy logs: {str(e)}")

@router.get("/logs/export")
def export_logs(
    format: str = Query("CSV", description="Export format (CSV or JSON)"),
    days: int = Query(30, description="Number of days of logs to export")
):
    """Export privacy logs"""
    try:
        content = LogService.export_logs(format=format, days=days)

        if format.upper() == "CSV":
            from fastapi.responses import Response
            return Response(
                content=content,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=privacy_logs.csv"}
            )
        else:
            from fastapi.responses import JSONResponse
            import json
            return JSONResponse(content=json.loads(content))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting logs: {str(e)}")