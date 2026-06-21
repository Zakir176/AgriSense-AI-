from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..database import get_db
from ..models.reading import FeedWaterReading
from ..schemas.reading import FeedWaterReadingCreate, FeedWaterReadingResponse, FeedWaterReadingUpdate, ReadingSummary
from ..services.rules_engine import check_reading_anomalies

router = APIRouter(prefix="/readings", tags=["Readings"])

@router.post("", response_model=FeedWaterReadingResponse, status_code=status.HTTP_201_CREATED)
def create_reading(reading: FeedWaterReadingCreate, db: Session = Depends(get_db)):
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
        water_litres=reading.water_litres
    )
    
    db_reading = FeedWaterReading(
        batch_id=reading.batch_id,
        date=reading.date,
        feed_kg=reading.feed_kg,
        water_litres=reading.water_litres,
        flagged_abnormal=flagged
    )
    
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

@router.get("", response_model=List[FeedWaterReadingResponse])
def list_readings(batch_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(FeedWaterReading)
    if batch_id is not None:
        query = query.filter(FeedWaterReading.batch_id == batch_id)
    return query.order_by(FeedWaterReading.date.desc()).all()

@router.get("/summary/{batch_id}", response_model=List[ReadingSummary])
def get_readings_summary(batch_id: int, db: Session = Depends(get_db)):
    # Return readings with calculated rolling averages and deviations for UI charts
    readings = db.query(FeedWaterReading).filter(
        FeedWaterReading.batch_id == batch_id
    ).order_by(FeedWaterReading.date.asc()).all()
    
    summaries = []
    for i, r in enumerate(readings):
        # Calculate 7d rolling average of the PREVIOUS 7 days (not including current)
        prev_readings = readings[max(0, i-7):i]
        
        avg_feed = sum(pr.feed_kg for pr in prev_readings) / len(prev_readings) if prev_readings else r.feed_kg
        avg_water = sum(pr.water_litres for pr in prev_readings) / len(prev_readings) if prev_readings else r.water_litres
        
        feed_dev = (r.feed_kg - avg_feed) / avg_feed if avg_feed > 0 else 0.0
        water_dev = (r.water_litres - avg_water) / avg_water if avg_water > 0 else 0.0
        
        summaries.append(
            ReadingSummary(
                date=r.date,
                feed_kg=r.feed_kg,
                water_litres=r.water_litres,
                feed_rolling_avg_7d=round(avg_feed, 2),
                water_rolling_avg_7d=round(avg_water, 2),
                feed_deviation_pct=round(feed_dev * 100, 2),
                water_deviation_pct=round(water_dev * 100, 2),
                flagged_abnormal=r.flagged_abnormal
            )
        )
    return summaries
