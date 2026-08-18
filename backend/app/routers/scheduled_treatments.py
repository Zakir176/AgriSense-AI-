from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timezone
import hashlib
import hmac

from ..config import settings
from ..database import get_db
from ..models.scheduled_treatment import ScheduledTreatment
from ..models.medication import MedicationEntry
from ..models.batch import Batch
from ..models.auth import User
from ..models.user_farm import UserFarmAssociation
from ..schemas.scheduled_treatment import (
    ScheduledTreatmentCreate, 
    ScheduledTreatmentResponse, 
    ScheduledTreatmentUpdate,
    DigitalSignoffRequest
)
from .auth import get_current_user, get_user_farm

"""
Scheduled Treatments Router
===========================
Provides endpoints for the Interactive Treatment Calendar & Biosecurity Sign-Off System.
Allows veterinarians and operators to prescribe, list, update, and digitally sign off on treatments.
Digitally signing off automatically creates an audited historical record in medication logs.
"""
router = APIRouter(prefix="/schedules", tags=["Scheduled Treatments"])

@router.post("", response_model=ScheduledTreatmentResponse, status_code=status.HTTP_201_CREATED)
def create_scheduled_treatment(entry: ScheduledTreatmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Creates a new scheduled treatment (e.g. vaccination, vitamin plan) for a specific batch.
    """
    batch = db.query(Batch).filter(Batch.id == entry.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to schedule treatments")

    prescriber = entry.prescribed_by or current_user.full_name or current_user.username

    db_entry = ScheduledTreatment(
        batch_id=entry.batch_id,
        title=entry.title,
        treatment_type=entry.treatment_type,
        scheduled_date=entry.scheduled_date,
        dosage=entry.dosage,
        notes=entry.notes,
        status=entry.status or "pending",
        remind_at=entry.remind_at,
        prescribed_by=prescriber,
        reminder_channel=entry.reminder_channel or "browser",
        phone_number=entry.phone_number
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("", response_model=List[ScheduledTreatmentResponse])
def list_scheduled_treatments(batch_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lists upcoming and historical scheduled treatments.
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

@router.get("/due-reminders", response_model=List[ScheduledTreatmentResponse])
def list_due_reminders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns pending scheduled treatments that are due today or overdue for active user farms.
    """
    today_val = date.today()
    return db.query(ScheduledTreatment).join(Batch).join(UserFarmAssociation, Batch.farm_id == UserFarmAssociation.farm_id).filter(
        UserFarmAssociation.user_id == current_user.id,
        ScheduledTreatment.status == "pending",
        ScheduledTreatment.scheduled_date <= today_val
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

@router.post("/{entry_id}/signoff", response_model=ScheduledTreatmentResponse)
def signoff_scheduled_treatment(entry_id: int, signoff: DigitalSignoffRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Digitally signs off on a scheduled treatment (vaccination/medication).
    Records administrator name, timestamp, signature hash, and compliance log.
    """
    db_entry = db.query(ScheduledTreatment).filter(ScheduledTreatment.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Scheduled treatment not found")
        
    batch = db.query(Batch).filter(Batch.id == db_entry.batch_id).first()
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to sign off treatments")
        
    if db_entry.status == "completed":
        raise HTTPException(status_code=400, detail="Treatment is already completed and signed off")
        
    admin_name = signoff.administered_by or current_user.full_name or current_user.username
    now_iso = datetime.now(timezone.utc).isoformat()  # timezone-aware (replaces deprecated utcnow)
    raw_sig = f"SIG-AGRI-{entry_id}-{admin_name}-{now_iso}"
    # HMAC-SHA256 keyed on SECRET_KEY — forgery requires knowledge of the server secret (F-17)
    sig_hash = signoff.digital_signature or hmac.new(
        settings.SECRET_KEY.encode(),
        raw_sig.encode(),
        hashlib.sha256,
    ).hexdigest()[:16].upper()

    db_entry.status = "completed"
    db_entry.completed_date = date.today()
    db_entry.administered_by = admin_name
    db_entry.digital_signature = sig_hash

    note_text = f"Signed off by {admin_name} [Sig: {sig_hash}]."
    if signoff.notes:
        note_text += f" Note: {signoff.notes}"

    med_entry = MedicationEntry(
        batch_id=db_entry.batch_id,
        date=date.today(),
        medicine_type=f"{db_entry.title} ({db_entry.treatment_type.capitalize()})",
        dosage=db_entry.dosage or "N/A",
        outcome_note=note_text
    )
    db.add(med_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.post("/{entry_id}/complete", response_model=ScheduledTreatmentResponse)
def complete_scheduled_treatment(entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Quick complete endpoint (defaults administrator to active user).
    """
    signoff_req = DigitalSignoffRequest(
        administered_by=current_user.full_name or current_user.username,
        notes="Quick complete sign-off"
    )
    return signoff_scheduled_treatment(entry_id, signoff_req, db, current_user)

