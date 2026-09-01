from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class MedicationEntryBase(BaseModel):
    batch_id: int
    date: date
    medicine_type: str = Field(..., max_length=200)
    dosage: str = Field(..., max_length=200)
    outcome_note: Optional[str] = Field(None, max_length=1000)

class MedicationEntryCreate(MedicationEntryBase):
    pass

class MedicationEntryUpdate(BaseModel):
    batch_id: Optional[int] = None
    date: Optional[date] = None
    medicine_type: Optional[str] = Field(None, max_length=200)
    dosage: Optional[str] = Field(None, max_length=200)
    outcome_note: Optional[str] = Field(None, max_length=1000)

class MedicationEntryResponse(MedicationEntryBase):
    id: int

    class Config:
        from_attributes = True
