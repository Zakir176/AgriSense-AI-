from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.audio import AudioConfig
from ..models.farm import Farm
from ..schemas.audio import AudioConfigResponse, AudioConfigUpdate
from .auth import get_current_user

router = APIRouter(prefix="/audio", tags=["Audio"])

@router.get("/config/{farm_id}", response_model=AudioConfigResponse)
def get_audio_config(farm_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Verify farm exists
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    config = db.query(AudioConfig).filter(AudioConfig.farm_id == farm_id).first()
    if not config:
        # Create default config if not exists
        config = AudioConfig(farm_id=farm_id, cough_threshold_pct=80.0, chirp_threshold_pct=65.0)
        db.add(config)
        db.commit()
        db.refresh(config)
        
    return config

@router.put("/config/{farm_id}", response_model=AudioConfigResponse)
def update_audio_config(farm_id: int, config_update: AudioConfigUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    config = db.query(AudioConfig).filter(AudioConfig.farm_id == farm_id).first()
    if not config:
        # Create it first
        config = AudioConfig(farm_id=farm_id, cough_threshold_pct=80.0, chirp_threshold_pct=65.0)
        db.add(config)
        db.commit()
        db.refresh(config)

    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)
    return config
