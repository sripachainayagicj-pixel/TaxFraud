from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db, SystemSettings
from ..models import SystemSettings as SettingsModel, SettingsUpdate

router = APIRouter()

@router.get("/settings", response_model=SettingsModel)
def get_settings(db: Session = Depends(get_db)):
    """Get current system settings"""
    try:
        settings = db.query(SystemSettings).first()

        if not settings:
            # Create default settings
            settings = SystemSettings()
            db.add(settings)
            db.commit()
            db.refresh(settings)

        return SettingsModel(
            data_retention_days=settings.data_retention_days,
            max_records_per_scan=settings.max_records_per_scan,
            risk_threshold=settings.risk_threshold,
            enable_encryption=settings.enable_encryption,
            enable_anonymization=settings.enable_anonymization,
            export_format=settings.export_format
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching settings: {str(e)}")

@router.post("/settings")
def update_settings(settings_update: SettingsUpdate, db: Session = Depends(get_db)):
    """Update system settings"""
    try:
        settings = db.query(SystemSettings).first()

        if not settings:
            settings = SystemSettings()
            db.add(settings)

        # Update only provided fields
        update_data = settings_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        db.commit()
        db.refresh(settings)

        return {"message": "Settings updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")