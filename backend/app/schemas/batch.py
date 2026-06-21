from pydantic import BaseModel
from datetime import date
from typing import Optional

class BatchBase(BaseModel):
    farm_id: int
    start_date: date
    bird_count: int
    breed: str
    status: Optional[str] = "active"

class BatchCreate(BatchBase):
    pass

class BatchUpdate(BaseModel):
    farm_id: Optional[int] = None
    start_date: Optional[date] = None
    bird_count: Optional[int] = None
    breed: Optional[str] = None
    status: Optional[str] = None

class BatchResponse(BatchBase):
    id: int

    class Config:
        from_attributes = True
