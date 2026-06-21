from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.alert import Alert
from ..schemas.alert import AlertResponse, AlertUpdate

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
def list_alerts(batch_id: Optional[int] = None, unacknowledged_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Alert)
    if batch_id is not None:
        query = query.filter(Alert.batch_id == batch_id)
    if unacknowledged_only:
        query = query.filter(Alert.acknowledged == False)
    return query.order_by(Alert.created_at.desc()).all()

@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: int, alert_update: AlertUpdate, db: Session = Depends(get_db)):
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert_update.acknowledged is not None:
        db_alert.acknowledged = alert_update.acknowledged
    db.commit()
    db.refresh(db_alert)
    return db_alert
