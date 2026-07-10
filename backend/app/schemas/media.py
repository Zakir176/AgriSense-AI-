from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class InferenceResultBase(BaseModel):
    bird_count_est: Optional[int] = None
    movement_score: Optional[float] = None
    low_activity_windows: Optional[List[Dict[str, Any]]] = None
    tracked_birds: Optional[List[Dict[str, Any]]] = None
    discrepancy_note: Optional[str] = None
    clustering_density_pct: Optional[float] = None
    spatial_dispersion_index: Optional[float] = None

class InferenceResultCreate(InferenceResultBase):
    media_clip_id: int

class InferenceResultResponse(InferenceResultBase):
    id: int
    media_clip_id: int

    class Config:
        from_attributes = True

class MediaClipBase(BaseModel):
    batch_id: int
    file_url: str

class MediaClipCreate(MediaClipBase):
    pass

class MediaClipResponse(MediaClipBase):
    id: int
    uploaded_at: datetime
    inference_result: Optional[InferenceResultResponse] = None

    class Config:
        from_attributes = True
