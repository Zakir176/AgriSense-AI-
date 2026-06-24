from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.medication import MedicationEntry
from ..schemas.medication import MedicationEntryCreate, MedicationEntryResponse, MedicationEntryUpdate

router = APIRouter(prefix="/medications", tags=["Medications"])

@router.post("", response_model=MedicationEntryResponse, status_code=status.HTTP_201_CREATED)
def create_medication_entry(entry: MedicationEntryCreate, db: Session = Depends(get_db)):
    db_entry = MedicationEntry(
        batch_id=entry.batch_id,
        date=entry.date,
        medicine_type=entry.medicine_type,
        dosage=entry.dosage,
        outcome_note=entry.outcome_note
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("", response_model=List[MedicationEntryResponse])
def list_medication_entries(batch_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(MedicationEntry)
    if batch_id is not None:
        query = query.filter(MedicationEntry.batch_id == batch_id)
    return query.order_by(MedicationEntry.date.desc()).all()

@router.put("/{entry_id}", response_model=MedicationEntryResponse)
def update_medication_entry(entry_id: int, entry: MedicationEntryUpdate, db: Session = Depends(get_db)):
    db_entry = db.query(MedicationEntry).filter(MedicationEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Medication entry not found")
        
    update_data = entry.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entry, key, value)
        
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication_entry(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(MedicationEntry).filter(MedicationEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Medication entry not found")
    db.delete(db_entry)
    db.commit()
    return
