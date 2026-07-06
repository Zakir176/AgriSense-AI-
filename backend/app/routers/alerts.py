from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.alert import Alert
from ..models.batch import Batch
from ..models.auth import User
from ..models.user_farm import UserFarmAssociation
from ..schemas.alert import AlertResponse, AlertUpdate
from .auth import get_current_user, get_user_farm

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
def list_alerts(batch_id: Optional[int] = None, unacknowledged_only: bool = False, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if batch_id is not None:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        get_user_farm(batch.farm_id, current_user, db)
        query = db.query(Alert).filter(Alert.batch_id == batch_id)
    else:
        # Return all alerts on farms associated with current_user
        query = db.query(Alert).join(Batch).join(UserFarmAssociation, Batch.farm_id == UserFarmAssociation.farm_id).filter(
            UserFarmAssociation.user_id == current_user.id
        )
        
    if unacknowledged_only:
        query = query.filter(Alert.acknowledged == False)
        
    return query.order_by(Alert.created_at.desc()).all()

@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: int, alert_update: AlertUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    batch = db.query(Batch).filter(Batch.id == db_alert.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to acknowledge alerts")
        
    if alert_update.acknowledged is not None:
        db_alert.acknowledged = alert_update.acknowledged
    db.commit()
    db.refresh(db_alert)
    return db_alert
