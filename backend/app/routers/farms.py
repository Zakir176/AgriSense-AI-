from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.farm import Farm
from ..schemas.farm import FarmCreate, FarmResponse, FarmUpdate

router = APIRouter(prefix="/farms", tags=["Farms"])

@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(farm: FarmCreate, db: Session = Depends(get_db)):
    db_farm = Farm(name=farm.name, location=farm.location)
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm

@router.get("", response_model=List[FarmResponse])
def list_farms(db: Session = Depends(get_db)):
    return db.query(Farm).all()

@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: int, db: Session = Depends(get_db)):
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return db_farm

@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(farm_id: int, farm: FarmUpdate, db: Session = Depends(get_db)):
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.name is not None:
        db_farm.name = farm.name
    if farm.location is not None:
        db_farm.location = farm.location
    db.commit()
    db.refresh(db_farm)
    return db_farm

@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(farm_id: int, db: Session = Depends(get_db)):
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    db.delete(db_farm)
    db.commit()
    return
