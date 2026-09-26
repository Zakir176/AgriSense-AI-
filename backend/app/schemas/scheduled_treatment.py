from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class ScheduledTreatmentBase(BaseModel):
    batch_id: int
    title: str = Field(..., max_length=300)
    treatment_type: str = Field(..., max_length=100)
    scheduled_date: date
    dosage: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field("pending", max_length=50)
    remind_at: Optional[datetime] = None
    prescribed_by: Optional[str] = Field(None, max_length=200)
    administered_by: Optional[str] = Field(None, max_length=200)
    digital_signature: Optional[str] = Field(None, max_length=64)
    reminder_channel: Optional[str] = Field("browser", max_length=50)
    phone_number: Optional[str] = Field(None, max_length=30)

class ScheduledTreatmentCreate(ScheduledTreatmentBase):
    pass

class ScheduledTreatmentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    treatment_type: Optional[str] = Field(None, max_length=100)
    scheduled_date: Optional[date] = None
    dosage: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None, max_length=50)
    completed_date: Optional[date] = None
    remind_at: Optional[datetime] = None
    prescribed_by: Optional[str] = Field(None, max_length=200)
    administered_by: Optional[str] = Field(None, max_length=200)
    digital_signature: Optional[str] = Field(None, max_length=64)
    reminder_channel: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=30)

class DigitalSignoffRequest(BaseModel):
    administered_by: str = Field(..., max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)
    digital_signature: Optional[str] = Field(None, max_length=64)

class ScheduledTreatmentResponse(ScheduledTreatmentBase):
    id: int
    completed_date: Optional[date] = None

    class Config:
        from_attributes = True

