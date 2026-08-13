from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging
import os
import uuid
from ..database import get_db
from ..config import settings
from ..models.media import MediaClip, InferenceResult
from ..models.batch import Batch
from ..models.auth import User
from ..models.user_farm import UserFarmAssociation
from ..schemas.media import MediaClipResponse
from ..services.inference_service import run_video_inference
from .auth import get_current_user, get_user_farm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inference", tags=["Inference"])

@router.post("/video", response_model=MediaClipResponse, status_code=status.HTTP_201_CREATED)
async def upload_video_for_inference(
    batch_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to upload files/run inference")

    # Verify directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Fix 1.8: Sanitise filename to prevent path traversal
    safe_filename = os.path.basename(file.filename or "upload")
    file_extension = os.path.splitext(safe_filename)[1].lower()

    # Fix 1.3a: Validate file extension against allowlist
    if file_extension not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file_extension}'. Allowed: {', '.join(sorted(settings.ALLOWED_VIDEO_EXTENSIONS))}"
        )

    # Fix 1.3b: Enforce maximum upload size (read in chunks, reject if oversized)
    max_bytes = settings.UPLOAD_MAX_MB * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {settings.UPLOAD_MAX_MB} MB."
        )

    # Save the file with a UUID name to avoid collisions and mask original filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception:
        logger.exception("Failed to save uploaded file to disk")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file. Please try again.")
        
    # Create MediaClip record
    db_media_clip = MediaClip(
        batch_id=batch_id,
        file_url=file_path
    )
    db.add(db_media_clip)
    db.flush()  # Obtain id before running inference
    
    # Run video inference
    try:
        inf_data = run_video_inference(file_path)
    except Exception:
        # Cleanup file if inference failed catastrophically and error out
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.exception("Video inference execution failed")
        raise HTTPException(status_code=500, detail="Video inference failed. Please try again.")
        
    # Create InferenceResult record
    # Calculate Expected Count based on batch count and readings mortality
    from ..models.reading import FeedWaterReading
    from ..models.alert import Alert
    
    cumulative_mortality = db.query(func.sum(FeedWaterReading.mortality_count)).filter(FeedWaterReading.batch_id == batch_id).scalar() or 0
    expected_count = max(0, batch.bird_count - cumulative_mortality)
    
    bird_count_est = inf_data["bird_count_est"]
    tracked_birds = inf_data["tracked_birds"]
    
    discrepancy_note = None
    if bird_count_est < expected_count:
        missing_count = expected_count - bird_count_est
        has_inactive = any(b["status"] == "inactive" for b in tracked_birds)
        if has_inactive:
            discrepancy_note = f"{missing_count} bird(s) missing. Detected potential mortality (lethargic/dead bird detected in visual)."
            alert_msg = f"Visual anomaly: {missing_count} bird(s) missing from expected flock. Lethargic/inactive bird detected in visual. Expected: {expected_count}, Detected: {bird_count_est}."
            new_alert = Alert(
                batch_id=batch_id,
                type="mortality",
                message=alert_msg,
                severity="critical",
                acknowledged=False
            )
            db.add(new_alert)
        else:
            discrepancy_note = f"{missing_count} bird(s) missing. Review for potential undocumented loss or theft."
            alert_msg = f"Visual anomaly: Population discrepancy detected. {missing_count} bird(s) missing with no signs of inactive/dead birds in visual. Expected: {expected_count}, Detected: {bird_count_est}. Suspected theft or undocumented loss."
            new_alert = Alert(
                batch_id=batch_id,
                type="manual",
                message=alert_msg,
                severity="warning",
                acknowledged=False
            )
            db.add(new_alert)
    elif bird_count_est > expected_count:
        discrepancy_note = f"Perfect match or higher density scan (Detected: {bird_count_est}, Expected: {expected_count})."
    else:
        discrepancy_note = f"Flock count match. Expected & Detected: {expected_count}."

    db_inference_result = InferenceResult(
        media_clip_id=db_media_clip.id,
        bird_count_est=bird_count_est,
        movement_score=inf_data["movement_score"],
        low_activity_windows=inf_data["low_activity_windows"],
        tracked_birds=tracked_birds,
        discrepancy_note=discrepancy_note,
        clustering_density_pct=inf_data.get("clustering_density_pct", 0.0),
        spatial_dispersion_index=inf_data.get("spatial_dispersion_index", 0.0)
    )
    db.add(db_inference_result)
    
    db.commit()
    db.refresh(db_media_clip)
    return db_media_clip

@router.get("/clips", response_model=List[MediaClipResponse])
def list_inference_clips(batch_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if batch_id is not None:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        get_user_farm(batch.farm_id, current_user, db)
        query = db.query(MediaClip).filter(MediaClip.batch_id == batch_id)
    else:
        # Return all clips on farms associated with current_user
        query = db.query(MediaClip).join(Batch).join(UserFarmAssociation, Batch.farm_id == UserFarmAssociation.farm_id).filter(
            UserFarmAssociation.user_id == current_user.id
        )
        
    return query.order_by(MediaClip.uploaded_at.desc()).all()
