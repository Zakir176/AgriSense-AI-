import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.audio import AudioConfig
from ..models.farm import Farm
from ..models.auth import User
from ..schemas.audio import AudioConfigResponse, AudioConfigUpdate
from .auth import get_current_user, get_user_farm

logger = logging.getLogger(__name__)

"""
Audio Telemetry Router
======================
Handles the configuration and classification of audio snippets for the Distress Call Classifier.
This router provides endpoints to upload short audio clips (.webm/.wav) and uses a simulated 
heuristic fallback (audio_classifier.py) to measure RMS volume and spectral centroids.
"""
router = APIRouter(prefix="/audio", tags=["Audio"])

@router.get("/config/{farm_id}", response_model=AudioConfigResponse)
def get_audio_config(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
 def get_audio_config(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve the current audio configuration for a specific farm.
    If no configuration exists, a default profile (80% cough threshold, 65% chirp threshold) is generated.
    """
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    get_user_farm(farm_id, current_user, db)

    config = db.query(AudioConfig).filter(AudioConfig.farm_id == farm_id).first()
    if not config:
        # Create default config if not exists
        config = AudioConfig(farm_id=farm_id, cough_threshold_pct=80.0, chirp_threshold_pct=65.0)
        db.add(config)
        db.commit()
        db.refresh(config)
        
    return config

@router.put("/config/{farm_id}", response_model=AudioConfigResponse)
def update_audio_config(farm_id: int, config_update: AudioConfigUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
 def update_audio_config(farm_id: int, config_update: AudioConfigUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update the audio telemetry thresholds (cough_threshold_pct and chirp_threshold_pct)
    for a specific farm. Adjusting these values calibrates the sensitivity of the anomaly detection.
    """
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    assoc = get_user_farm(farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to update audio config")
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

import os
import shutil
import uuid
from fastapi import UploadFile, File, Form
from ..config import settings
from ..services.audio_classifier import classify_audio_snippet
from ..schemas.audio import AudioClassificationResponse

@router.post("/classify", response_model=AudioClassificationResponse)
def classify_audio(
    farm_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Endpoint for uploading raw audio telemetry snippets. 
    The audio is saved to a temporary file and passed to the heuristic audio classifier, 
    which assesses the likelihood of respiratory distress (coughing/sneezing) or environmental stress (loud chirping).
    The temporary file is deleted immediately after classification.
    """
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    config = db.query(AudioConfig).filter(AudioConfig.farm_id == farm_id).first()
    if not config:
        config = AudioConfig(farm_id=farm_id, cough_threshold_pct=80.0, chirp_threshold_pct=65.0)

    # ── Input validation (F-11) ────────────────────────────────────────────────
    ALLOWED_AUDIO_EXTENSIONS = frozenset({".webm", ".wav", ".mp3", ".ogg", ".m4a"})
    AUDIO_MAX_MB = 10

    safe_filename = os.path.basename(file.filename or "audio")
    file_extension = os.path.splitext(safe_filename)[1].lower()

    if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Allowed: .webm, .wav, .mp3, .ogg, .m4a",
        )

    max_bytes = AUDIO_MAX_MB * 1024 * 1024
    content = file.file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large. Maximum size is {AUDIO_MAX_MB} MB.",
        )

    # ── Persist to disk ────────────────────────────────────────────────────────
    # Verify directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    unique_filename = f"audio_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception:
        logger.exception("Failed to save uploaded audio file")
        raise HTTPException(status_code=500, detail="Failed to save uploaded audio file. Please try again.")

    try:
        result = classify_audio_snippet(file_path, config)
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.exception("Audio classification failed")
        raise HTTPException(status_code=500, detail="Audio classification failed. Please try again.")
        
    # Cleanup temp file after processing
    if os.path.exists(file_path):
        os.remove(file_path)
        
    return result
