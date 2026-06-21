from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
from ..database import get_db
from ..config import settings
from ..models.media import MediaClip, InferenceResult
from ..schemas.media import MediaClipResponse
from ..services.inference_service import run_video_inference

router = APIRouter(prefix="/inference", tags=["Inference"])

@router.post("/video", response_model=MediaClipResponse, status_code=status.HTTP_201_CREATED)
def upload_video_for_inference(
    batch_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verify directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save the file
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")
        
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
    except Exception as e:
        # Cleanup file if inference failed catastrophically and error out
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Inference execution failed: {e}")
        
    # Create InferenceResult record
    db_inference_result = InferenceResult(
        media_clip_id=db_media_clip.id,
        bird_count_est=inf_data["bird_count_est"],
        movement_score=inf_data["movement_score"],
        low_activity_windows=inf_data["low_activity_windows"]
    )
    db.add(db_inference_result)
    
    db.commit()
    db.refresh(db_media_clip)
    return db_media_clip

@router.get("/clips", response_model=List[MediaClipResponse])
def list_inference_clips(batch_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(MediaClip)
    if batch_id is not None:
        query = query.filter(MediaClip.batch_id == batch_id)
    return query.order_by(MediaClip.uploaded_at.desc()).all()
