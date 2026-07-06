from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import SettingUpdate, SettingOut, MessageResponse
from app.models.models import Settings as SettingsModel

router = APIRouter(prefix="/settings", tags=["Settings"])

DEFAULT_SETTINGS = {
    "theme": "light",
    "openai_api_key": "",
    "organization_name": "Government Legal Services",
    "case_number_prefix": "LA",
}


def _ensure_defaults(db: Session):
    for key, value in DEFAULT_SETTINGS.items():
        existing = db.query(SettingsModel).filter(SettingsModel.key == key).first()
        if not existing:
            db.add(SettingsModel(key=key, value=str(value)))
    db.commit()


@router.get("/", response_model=List[SettingOut])
def get_all_settings(db: Session = Depends(get_db)):
    _ensure_defaults(db)
    return db.query(SettingsModel).all()


@router.put("/", response_model=SettingOut)
def upsert_setting(data: SettingUpdate, db: Session = Depends(get_db)):
    existing = db.query(SettingsModel).filter(SettingsModel.key == data.key).first()
    if existing:
        existing.value = data.value
        db.commit()
        db.refresh(existing)
        return existing
    new_setting = SettingsModel(key=data.key, value=data.value)
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    return new_setting


@router.get("/{key}", response_model=SettingOut)
def get_setting(key: str, db: Session = Depends(get_db)):
    _ensure_defaults(db)
    setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
    if not setting:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return setting
