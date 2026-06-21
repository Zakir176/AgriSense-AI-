from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.batch import Batch
from ..schemas.batch import BatchCreate, BatchResponse, BatchUpdate

router = APIRouter(prefix="/batches", tags=["Batches"])

@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(batch: BatchCreate, db: Session = Depends(get_db)):
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
    return db_batch

@router.get("", response_model=List[BatchResponse])
def list_batches(farm_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Batch)
    if farm_id is not None:
        query = query.filter(Batch.farm_id == farm_id)
    return query.all()

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return db_batch

@router.put("/{batch_id}", response_model=BatchResponse)
def update_batch(batch_id: int, batch: BatchUpdate, db: Session = Depends(get_db)):
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    update_data = batch.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_batch, key, value)
        
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    db.delete(db_batch)
    db.commit()
    return
