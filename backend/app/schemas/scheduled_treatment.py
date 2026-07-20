from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ScheduledTreatmentBase(BaseModel):
    batch_id: int
    title: str
    treatment_type: str
    scheduled_date: date
    dosage: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "pending"
    remind_at: Optional[datetime] = None

class ScheduledTreatmentCreate(ScheduledTreatmentBase):
    pass

class ScheduledTreatmentUpdate(BaseModel):
    title: Optional[str] = None
    treatment_type: Optional[str] = None
    scheduled_date: Optional[date] = None
    dosage: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    completed_date: Optional[date] = None
    remind_at: Optional[datetime] = None

class ScheduledTreatmentResponse(ScheduledTreatmentBase):
    id: int
    completed_date: Optional[date] = None

    class Config:
        from_attributes = True
