from pydantic import BaseModel
from datetime import date
from typing import Optional

class MedicationEntryBase(BaseModel):
    batch_id: int
    date: date
    medicine_type: str
    dosage: str
    outcome_note: Optional[str] = None

class MedicationEntryCreate(MedicationEntryBase):
    pass

class MedicationEntryUpdate(BaseModel):
    batch_id: Optional[int] = None
    date: Optional[date] = None
    medicine_type: Optional[str] = None
    dosage: Optional[str] = None
    outcome_note: Optional[str] = None

class MedicationEntryResponse(MedicationEntryBase):
    id: int

    class Config:
        from_attributes = True
