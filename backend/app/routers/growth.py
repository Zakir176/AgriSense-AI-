from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.growth import GrowthSample
from ..models.batch import Batch
from ..models.auth import User
from ..models.user_farm import UserFarmAssociation
from ..schemas.growth import GrowthSampleCreate, GrowthSampleResponse, GrowthRateSummary, GrowthSampleUpdate
from .auth import get_current_user, get_user_farm

router = APIRouter(prefix="/growth", tags=["Growth"])

@router.post("", response_model=GrowthSampleResponse, status_code=status.HTTP_201_CREATED)
def create_growth_sample(sample: GrowthSampleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == sample.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to log growth samples")

    # Check if a sample exists for this batch and date
    existing = db.query(GrowthSample).filter(
        GrowthSample.batch_id == sample.batch_id,
        GrowthSample.date == sample.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Growth sample already exists for this date and batch")
        
    db_sample = GrowthSample(
        batch_id=sample.batch_id,
        date=sample.date,
        avg_weight_g=sample.avg_weight_g,
        sample_size=sample.sample_size
    )
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample

@router.get("", response_model=List[GrowthSampleResponse])
def list_growth_samples(batch_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if batch_id is not None:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        get_user_farm(batch.farm_id, current_user, db)
        return db.query(GrowthSample).filter(GrowthSample.batch_id == batch_id).order_by(GrowthSample.date.desc()).all()
        
    # Return all growth samples on farms associated with current_user
    return db.query(GrowthSample).join(Batch).join(UserFarmAssociation, Batch.farm_id == UserFarmAssociation.farm_id).filter(
        UserFarmAssociation.user_id == current_user.id
    ).order_by(GrowthSample.date.desc()).all()

@router.get("/summary/{batch_id}", response_model=List[GrowthRateSummary])
def get_growth_summary(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        return []
        
    get_user_farm(batch.farm_id, current_user, db)
    
    samples = db.query(GrowthSample).filter(
        GrowthSample.batch_id == batch_id
    ).order_by(GrowthSample.date.asc()).all()
    
    summaries = []
    for i, s in enumerate(samples):
        growth_rate = 0.0
        if i > 0:
            prev_s = samples[i-1]
            days_diff = (s.date - prev_s.date).days
            if days_diff > 0:
                growth_rate = (s.avg_weight_g - prev_s.avg_weight_g) / days_diff
                
        summaries.append(
            GrowthRateSummary(
                batch_id=s.batch_id,
                date=s.date,
                avg_weight_g=s.avg_weight_g,
                sample_size=s.sample_size,
                growth_rate_g_per_day=round(growth_rate, 2)
            )
        )
    return summaries

@router.put("/{sample_id}", response_model=GrowthSampleResponse)
def update_growth_sample(sample_id: int, sample: GrowthSampleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_sample = db.query(GrowthSample).filter(GrowthSample.id == sample_id).first()
    if not db_sample:
        raise HTTPException(status_code=404, detail="Growth sample not found")
        
    batch = db.query(Batch).filter(Batch.id == db_sample.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to update growth samples")
    
    update_data = sample.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sample, key, value)
    
    db.commit()
    db.refresh(db_sample)
    return db_sample

@router.delete("/{sample_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_growth_sample(sample_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_sample = db.query(GrowthSample).filter(GrowthSample.id == sample_id).first()
    if not db_sample:
        raise HTTPException(status_code=404, detail="Growth sample not found")
        
    batch = db.query(Batch).filter(Batch.id == db_sample.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to delete growth samples")
        
    db.delete(db_sample)
    db.commit()
    return
