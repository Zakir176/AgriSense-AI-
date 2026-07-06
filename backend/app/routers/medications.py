from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.medication import MedicationEntry
from ..models.batch import Batch
from ..models.auth import User
from ..models.user_farm import UserFarmAssociation
from ..schemas.medication import MedicationEntryCreate, MedicationEntryResponse, MedicationEntryUpdate
from .auth import get_current_user, get_user_farm

router = APIRouter(prefix="/medications", tags=["Medications"])

@router.post("", response_model=MedicationEntryResponse, status_code=status.HTTP_201_CREATED)
def create_medication_entry(entry: MedicationEntryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == entry.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to log medications")

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
def list_medication_entries(batch_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if batch_id is not None:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        get_user_farm(batch.farm_id, current_user, db)
        return db.query(MedicationEntry).filter(MedicationEntry.batch_id == batch_id).order_by(MedicationEntry.date.desc()).all()
        
    # Return all medication entries on farms associated with current_user
    return db.query(MedicationEntry).join(Batch).join(UserFarmAssociation, Batch.farm_id == UserFarmAssociation.farm_id).filter(
        UserFarmAssociation.user_id == current_user.id
    ).order_by(MedicationEntry.date.desc()).all()

@router.put("/{entry_id}", response_model=MedicationEntryResponse)
def update_medication_entry(entry_id: int, entry: MedicationEntryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_entry = db.query(MedicationEntry).filter(MedicationEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Medication entry not found")
        
    batch = db.query(Batch).filter(Batch.id == db_entry.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to update medications")
        
    update_data = entry.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entry, key, value)
        
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication_entry(entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_entry = db.query(MedicationEntry).filter(MedicationEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Medication entry not found")
        
    batch = db.query(Batch).filter(Batch.id == db_entry.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to delete medications")
        
    db.delete(db_entry)
    db.commit()
    return
