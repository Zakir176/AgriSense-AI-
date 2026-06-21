from pydantic import BaseModel
from datetime import date
from typing import Optional

class GrowthSampleBase(BaseModel):
    batch_id: int
    date: date
    avg_weight_g: float
    sample_size: int

class GrowthSampleCreate(GrowthSampleBase):
    pass

class GrowthSampleUpdate(BaseModel):
    batch_id: Optional[int] = None
    date: Optional[date] = None
    avg_weight_g: Optional[float] = None
    sample_size: Optional[int] = None

class GrowthSampleResponse(GrowthSampleBase):
    id: int

    class Config:
        from_attributes = True

class GrowthRateSummary(BaseModel):
    batch_id: int
    date: date
    avg_weight_g: float
    sample_size: int
    growth_rate_g_per_day: float
