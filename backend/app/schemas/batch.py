from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class BatchBase(BaseModel):
    farm_id: int
    start_date: date
    bird_count: int
    breed: str = Field(..., max_length=200)
    status: Optional[str] = Field("active", max_length=50)

class BatchCreate(BatchBase):
    pass

class BatchUpdate(BaseModel):
    farm_id: Optional[int] = None
    start_date: Optional[date] = None
    bird_count: Optional[int] = None
    breed: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, max_length=50)

class BatchResponse(BatchBase):
    id: int

    class Config:
        from_attributes = True
