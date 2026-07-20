from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models.scheduled_treatment import ScheduledTreatment
from ..models.medication import MedicationEntry
from ..models.batch import Batch
from ..models.auth import User
from ..models.user_farm import UserFarmAssociation
from ..schemas.scheduled_treatment import ScheduledTreatmentCreate, ScheduledTreatmentResponse, ScheduledTreatmentUpdate
from .auth import get_current_user, get_user_farm

"""
Scheduled Treatments Router
===========================
Provides endpoints for the Interactive Treatment Calendar. 
Allows operators to plan, list, update, and complete future vaccinations or medication schedules.
Completing a scheduled treatment automatically archives it into the historical medications log.
"""
router = APIRouter(prefix="/schedules", tags=["Scheduled Treatments"])

@router.post("", response_model=ScheduledTreatmentResponse, status_code=status.HTTP_201_CREATED)
def create_scheduled_treatment(entry: ScheduledTreatmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Creates a new scheduled treatment (e.g. vaccination, vitamin plan) for a specific batch.
    Requires Operator or Owner role. Supports optional browser push notification intent via 'remind_at'.
    """
    batch = db.query(Batch).filter(Batch.id == entry.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to schedule treatments")

    db_entry = ScheduledTreatment(
        batch_id=entry.batch_id,
        title=entry.title,
        treatment_type=entry.treatment_type,
        scheduled_date=entry.scheduled_date,
        dosage=entry.dosage,
        notes=entry.notes,
        status=entry.status,
        remind_at=entry.remind_at
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("", response_model=List[ScheduledTreatmentResponse])
def list_scheduled_treatments(batch_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lists upcoming and historical scheduled treatments.
    If 'batch_id' is provided, filters for that specific batch. Otherwise, lists all schedules across the user's farms.
    """
    if batch_id is not None:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        get_user_farm(batch.farm_id, current_user, db)
        return db.query(ScheduledTreatment).filter(ScheduledTreatment.batch_id == batch_id).order_by(ScheduledTreatment.scheduled_date.asc()).all()
        
    return db.query(ScheduledTreatment).join(Batch).join(UserFarmAssociation, Batch.farm_id == UserFarmAssociation.farm_id).filter(
        UserFarmAssociation.user_id == current_user.id
    ).order_by(ScheduledTreatment.scheduled_date.asc()).all()

@router.put("/{entry_id}", response_model=ScheduledTreatmentResponse)
def update_scheduled_treatment(entry_id: int, entry: ScheduledTreatmentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_entry = db.query(ScheduledTreatment).filter(ScheduledTreatment.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Scheduled treatment not found")
        
    batch = db.query(Batch).filter(Batch.id == db_entry.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to update scheduled treatments")
        
    update_data = entry.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entry, key, value)
        
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheduled_treatment(entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_entry = db.query(ScheduledTreatment).filter(ScheduledTreatment.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Scheduled treatment not found")
        
    batch = db.query(Batch).filter(Batch.id == db_entry.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to delete scheduled treatments")
        
    db.delete(db_entry)
    db.commit()
    return

@router.post("/{entry_id}/complete", response_model=ScheduledTreatmentResponse)
def complete_scheduled_treatment(entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Marks a scheduled treatment as 'completed'.
    This automatically generates a historical MedicationEntry log for the batch with the applied dosage and outcome notes.
    """
    db_entry = db.query(ScheduledTreatment).filter(ScheduledTreatment.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Scheduled treatment not found")
        
    batch = db.query(Batch).filter(Batch.id == db_entry.batch_id).first()
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to complete treatments")
        
    if db_entry.status == "completed":
        raise HTTPException(status_code=400, detail="Treatment is already completed")
        
    # Mark scheduled as completed
    db_entry.status = "completed"
    db_entry.completed_date = date.today()
    
    # Create the corresponding medication entry history log
    med_entry = MedicationEntry(
        batch_id=db_entry.batch_id,
        date=date.today(),
        medicine_type=f"{db_entry.title} ({db_entry.treatment_type.capitalize()})",
        dosage=db_entry.dosage or "N/A",
        outcome_note=f"Completed from schedule: {db_entry.notes or ''}".strip()
    )
    db.add(med_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry
