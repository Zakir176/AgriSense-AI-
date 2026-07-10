from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..database import get_db
from ..models.reading import FeedWaterReading
from ..models.batch import Batch
from ..models.growth import GrowthSample
from ..schemas.reading import FeedWaterReadingCreate, FeedWaterReadingResponse, FeedWaterReadingUpdate, ReadingSummary
from ..services.rules_engine import check_reading_anomalies
from .auth import get_current_user, get_user_farm
from ..models.auth import User
from ..models.user_farm import UserFarmAssociation

router = APIRouter(prefix="/readings", tags=["Readings"])

@router.post("", response_model=FeedWaterReadingResponse, status_code=status.HTTP_201_CREATED)
def create_reading(reading: FeedWaterReadingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == reading.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to log readings")

    # Check if a reading already exists for this batch and date
    existing = db.query(FeedWaterReading).filter(
        FeedWaterReading.batch_id == reading.batch_id,
        FeedWaterReading.date == reading.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Reading already exists for this date and batch")
        
    # Check for anomaly using rules engine
    flagged = check_reading_anomalies(
        db=db,
        batch_id=reading.batch_id,
        reading_date=reading.date,
        feed_kg=reading.feed_kg,
        water_litres=reading.water_litres,
        mortality_count=reading.mortality_count or 0
    )
    
    db_reading = FeedWaterReading(
        batch_id=reading.batch_id,
        date=reading.date,
        feed_kg=reading.feed_kg,
        water_litres=reading.water_litres,
        mortality_count=reading.mortality_count or 0,
        flagged_abnormal=flagged
    )
    
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

@router.get("", response_model=List[FeedWaterReadingResponse])
def list_readings(batch_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if batch_id is not None:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        get_user_farm(batch.farm_id, current_user, db)
        return db.query(FeedWaterReading).filter(FeedWaterReading.batch_id == batch_id).order_by(FeedWaterReading.date.desc()).all()
        
    # Return all readings for batches on farms associated with current_user
    return db.query(FeedWaterReading).join(Batch).join(UserFarmAssociation, Batch.farm_id == UserFarmAssociation.farm_id).filter(
        UserFarmAssociation.user_id == current_user.id
    ).order_by(FeedWaterReading.date.desc()).all()

@router.get("/summary/{batch_id}", response_model=List[ReadingSummary])
def get_readings_summary(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        return []
    get_user_farm(batch.farm_id, current_user, db)

    readings = db.query(FeedWaterReading).filter(
        FeedWaterReading.batch_id == batch_id
    ).order_by(FeedWaterReading.date.asc()).all()
    
    growth_samples = db.query(GrowthSample).filter(
        GrowthSample.batch_id == batch_id
    ).order_by(GrowthSample.date.asc()).all()
    
    summaries = []
    cumulative_mortality = 0
    cumulative_feed_kg = 0.0

    for i, r in enumerate(readings):
        cumulative_mortality += (r.mortality_count or 0)
        cumulative_feed_kg += r.feed_kg

        # Calculate 7d rolling average of the PREVIOUS 7 days (not including current)
        prev_readings = readings[max(0, i-7):i]
        
        avg_feed = sum(pr.feed_kg for pr in prev_readings) / len(prev_readings) if prev_readings else r.feed_kg
        avg_water = sum(pr.water_litres for pr in prev_readings) / len(prev_readings) if prev_readings else r.water_litres
        
        feed_dev = (r.feed_kg - avg_feed) / avg_feed if avg_feed > 0 else 0.0
        water_dev = (r.water_litres - avg_water) / avg_water if avg_water > 0 else 0.0
        
        # Calculate FCR
        fcr = None
        current_birds = max(1, batch.bird_count - cumulative_mortality)
        
        # Find latest growth sample on or before this date
        latest_growth = None
        for gs in growth_samples:
            if gs.date <= r.date:
                latest_growth = gs
            else:
                break
                
        if latest_growth and cumulative_feed_kg > 0:
            # Approximate flock weight gain
            # initial weight assumed 40g (0.04kg)
            weight_gain_per_bird_kg = (latest_growth.avg_weight_g / 1000.0) - 0.04
            total_weight_gain_kg = weight_gain_per_bird_kg * current_birds
            if total_weight_gain_kg > 0:
                fcr = cumulative_feed_kg / total_weight_gain_kg

        summaries.append(
            ReadingSummary(
                date=r.date,
                feed_kg=r.feed_kg,
                water_litres=r.water_litres,
                mortality_count=r.mortality_count or 0,
                cumulative_mortality=cumulative_mortality,
                feed_conversion_ratio=round(fcr, 2) if fcr else None,
                feed_rolling_avg_7d=round(avg_feed, 2),
                water_rolling_avg_7d=round(avg_water, 2),
                feed_deviation_pct=round(feed_dev * 100, 2),
                water_deviation_pct=round(water_dev * 100, 2),
                flagged_abnormal=r.flagged_abnormal,
                temperature_celsius=r.temperature_celsius
            )
        )
    return summaries

@router.put("/{reading_id}", response_model=FeedWaterReadingResponse)
def update_reading(reading_id: int, reading: FeedWaterReadingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_reading = db.query(FeedWaterReading).filter(FeedWaterReading.id == reading_id).first()
    if not db_reading:
        raise HTTPException(status_code=404, detail="Reading not found")
        
    batch = db.query(Batch).filter(Batch.id == db_reading.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to update readings")
    
    update_data = reading.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_reading, key, value)
    
    db.commit()
    db.refresh(db_reading)
    return db_reading

@router.delete("/{reading_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reading(reading_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_reading = db.query(FeedWaterReading).filter(FeedWaterReading.id == reading_id).first()
    if not db_reading:
        raise HTTPException(status_code=404, detail="Reading not found")
        
    batch = db.query(Batch).filter(Batch.id == db_reading.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to delete readings")
        
    db.delete(db_reading)
    db.commit()
    return
