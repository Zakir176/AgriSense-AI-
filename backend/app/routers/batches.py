from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.batch import Batch
from ..models.user_farm import UserFarmAssociation
from ..schemas.batch import BatchCreate, BatchResponse, BatchUpdate
from .auth import get_current_user, get_user_farm

router = APIRouter(prefix="/batches", tags=["Batches"])

@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(batch: BatchCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to create batches")
        
    db_batch = Batch(
        farm_id=batch.farm_id,
        start_date=batch.start_date,
        bird_count=batch.bird_count,
        breed=batch.breed,
        status=batch.status
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    
    # Auto-generate standard broiler vaccination schedule
    from datetime import timedelta
    from ..models.scheduled_treatment import ScheduledTreatment
    
    default_schedules = [
        {"day": 1, "title": "Marek's Vaccine", "type": "vaccine", "notes": "Hatchery (often pre-administered)"},
        {"day": 7, "title": "Gumboro (Dose 1)", "type": "vaccine", "notes": "Water/Oral administration"},
        {"day": 14, "title": "Newcastle (Dose 1)", "type": "vaccine", "notes": "Ocular or Water administration"},
        {"day": 21, "title": "Gumboro (Dose 2)", "type": "vaccine", "notes": "Water/Oral administration"},
        {"day": 28, "title": "Newcastle (Dose 2)", "type": "vaccine", "notes": "Water/Oral administration"}
    ]
    
    for sched in default_schedules:
        target_date = db_batch.start_date + timedelta(days=sched["day"] - 1)
        db_schedule = ScheduledTreatment(
            batch_id=db_batch.id,
            title=sched["title"],
            treatment_type=sched["type"],
            scheduled_date=target_date,
            notes=sched["notes"]
        )
        db.add(db_schedule)
        
    db.commit()
    
    return db_batch

@router.get("", response_model=List[BatchResponse])
def list_batches(farm_id: Optional[int] = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if farm_id is not None:
        get_user_farm(farm_id, current_user, db)
        return db.query(Batch).filter(Batch.farm_id == farm_id).all()
        
    # Return all batches for all farms associated with current_user
    return db.query(Batch).join(UserFarmAssociation, Batch.farm_id == UserFarmAssociation.farm_id).filter(
        UserFarmAssociation.user_id == current_user.id
    ).all()

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    get_user_farm(db_batch.farm_id, current_user, db)
    return db_batch

@router.put("/{batch_id}", response_model=BatchResponse)
def update_batch(batch_id: int, batch: BatchUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(db_batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to update batches")
        
    # Ensure they aren't trying to change farm_id to one they don't have access to
    if batch.farm_id is not None and batch.farm_id != db_batch.farm_id:
        get_user_farm(batch.farm_id, current_user, db)
        
    update_data = batch.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_batch, key, value)
        
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(batch_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(db_batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to delete batches")
        
    db.delete(db_batch)
    db.commit()
    return
