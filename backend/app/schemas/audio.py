from pydantic import BaseModel, Field

class AudioConfigBase(BaseModel):
    cough_threshold_pct: float = Field(..., ge=0, le=100)
    chirp_threshold_pct: float = Field(..., ge=0, le=100)

class AudioConfigCreate(AudioConfigBase):
    pass

class AudioConfigUpdate(BaseModel):
    cough_threshold_pct: float | None = Field(None, ge=0, le=100)
    chirp_threshold_pct: float | None = Field(None, ge=0, le=100)

class AudioConfigResponse(AudioConfigBase):
    id: int
    farm_id: int

    class Config:
        from_attributes = True

class AudioClassificationResponse(BaseModel):
    distressProb: int
    severity: str
    dominantPeak: str
    cohesion: int
    description: str
