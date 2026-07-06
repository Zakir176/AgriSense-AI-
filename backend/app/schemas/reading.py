from pydantic import BaseModel
from datetime import date
from typing import Optional

class FeedWaterReadingBase(BaseModel):
    batch_id: int
    date: date
    feed_kg: float
    water_litres: float
    mortality_count: Optional[int] = 0
    flagged_abnormal: Optional[bool] = False

class FeedWaterReadingCreate(FeedWaterReadingBase):
    pass

class FeedWaterReadingUpdate(BaseModel):
    batch_id: Optional[int] = None
    date: Optional[date] = None
    feed_kg: Optional[float] = None
    water_litres: Optional[float] = None
    mortality_count: Optional[int] = None
    flagged_abnormal: Optional[bool] = None

class FeedWaterReadingResponse(FeedWaterReadingBase):
    id: int

    class Config:
        from_attributes = True

class ReadingSummary(BaseModel):
    date: date
    feed_kg: float
    water_litres: float
    mortality_count: int
    cumulative_mortality: int
    feed_conversion_ratio: Optional[float] = None
    feed_rolling_avg_7d: float
    water_rolling_avg_7d: float
    feed_deviation_pct: float
    water_deviation_pct: float
    flagged_abnormal: bool
