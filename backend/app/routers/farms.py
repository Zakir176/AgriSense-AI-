from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.farm import Farm
from ..models.auth import User
from ..models.user_farm import UserFarmAssociation
from ..schemas.farm import FarmCreate, FarmResponse, FarmUpdate, FarmMemberAdd, FarmMemberUpdate, FarmMemberResponse
from .auth import get_current_user, get_user_farm

router = APIRouter(prefix="/farms", tags=["Farms"])

@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(farm: FarmCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_farm = Farm(name=farm.name, location=farm.location)
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    
    # Create UserFarmAssociation as owner
    assoc = UserFarmAssociation(user_id=current_user.id, farm_id=db_farm.id, role="owner")
    db.add(assoc)
    db.commit()
    
    db_farm.role = "owner"
    return db_farm

@router.get("", response_model=List[FarmResponse])
def list_farms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Return only farms where the user is associated
    farms = db.query(Farm).join(UserFarmAssociation).filter(UserFarmAssociation.user_id == current_user.id).all()
    for f in farms:
        assoc = db.query(UserFarmAssociation).filter(
            UserFarmAssociation.user_id == current_user.id,
            UserFarmAssociation.farm_id == f.id
        ).first()
        f.role = assoc.role if assoc else None
    return farms

@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # First check if user is associated
    assoc = get_user_farm(farm_id, current_user, db)
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    db_farm.role = assoc.role
    return db_farm

@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(farm_id: int, farm: FarmUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only owner role can update
    assoc = get_user_farm(farm_id, current_user, db)
    if assoc.role != "owner":
        raise HTTPException(status_code=403, detail="Only farm owners can update farm details")
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
def delete_farm(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only owner role can delete
    assoc = get_user_farm(farm_id, current_user, db)
    if assoc.role != "owner":
        raise HTTPException(status_code=403, detail="Only farm owners can delete farms")
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    db.delete(db_farm)
    db.commit()
    return

@router.get("/{farm_id}/members", response_model=List[FarmMemberResponse])
def list_farm_members(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify current user has access to the farm
    get_user_farm(farm_id, current_user, db)
    
    # Query associations with User details
    members = db.query(UserFarmAssociation).filter(UserFarmAssociation.farm_id == farm_id).all()
    
    response = []
    for m in members:
        # Fetch username and full_name
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            response.append(FarmMemberResponse(
                user_id=m.user_id,
                username=user.username,
                full_name=user.full_name,
                role=m.role
            ))
    return response

@router.post("/{farm_id}/members", response_model=FarmMemberResponse, status_code=status.HTTP_201_CREATED)
def add_farm_member(farm_id: int, member: FarmMemberAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify current user is owner
    assoc = get_user_farm(farm_id, current_user, db)
    if assoc.role != "owner":
        raise HTTPException(status_code=403, detail="Only farm owners can add members")
        
    # Check if target user exists
    target_user = db.query(User).filter(User.username == member.username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User account with this username does not exist")
        
    # Check if association already exists
    existing = db.query(UserFarmAssociation).filter(
        UserFarmAssociation.farm_id == farm_id,
        UserFarmAssociation.user_id == target_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already associated with this farm")
        
    # Create association
    new_assoc = UserFarmAssociation(
        user_id=target_user.id,
        farm_id=farm_id,
        role=member.role
    )
    db.add(new_assoc)
    db.commit()
    db.refresh(new_assoc)
    
    return FarmMemberResponse(
        user_id=new_assoc.user_id,
        username=target_user.username,
        full_name=target_user.full_name,
        role=new_assoc.role
    )

@router.put("/{farm_id}/members/{user_id}", response_model=FarmMemberResponse)
def update_farm_member(farm_id: int, user_id: int, member_update: FarmMemberUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify current user is owner
    assoc = get_user_farm(farm_id, current_user, db)
    if assoc.role != "owner":
        raise HTTPException(status_code=403, detail="Only farm owners can update member roles")
        
    # Find association to update
    target_assoc = db.query(UserFarmAssociation).filter(
        UserFarmAssociation.farm_id == farm_id,
        UserFarmAssociation.user_id == user_id
    ).first()
    if not target_assoc:
        raise HTTPException(status_code=404, detail="Member association not found")
        
    # Check if demoting the only owner
    if target_assoc.role == "owner" and member_update.role != "owner":
        owner_count = db.query(UserFarmAssociation).filter(
            UserFarmAssociation.farm_id == farm_id,
            UserFarmAssociation.role == "owner"
        ).count()
        if owner_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot update role: this farm must have at least one owner")
            
    target_assoc.role = member_update.role
    db.commit()
    db.refresh(target_assoc)
    
    target_user = db.query(User).filter(User.id == user_id).first()
    return FarmMemberResponse(
        user_id=target_assoc.user_id,
        username=target_user.username if target_user else "unknown",
        full_name=target_user.full_name if target_user else None,
        role=target_assoc.role
    )

@router.delete("/{farm_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_farm_member(farm_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify current user is owner OR is removing themselves
    assoc = get_user_farm(farm_id, current_user, db)
    is_self = current_user.id == user_id
    
    if assoc.role != "owner" and not is_self:
        raise HTTPException(status_code=403, detail="Only farm owners can remove other members")
        
    # Find association to delete
    target_assoc = db.query(UserFarmAssociation).filter(
        UserFarmAssociation.farm_id == farm_id,
        UserFarmAssociation.user_id == user_id
    ).first()
    if not target_assoc:
        raise HTTPException(status_code=404, detail="Member association not found")
        
    # Prevent removing the only owner
    if target_assoc.role == "owner":
        owner_count = db.query(UserFarmAssociation).filter(
            UserFarmAssociation.farm_id == farm_id,
            UserFarmAssociation.role == "owner"
        ).count()
        if owner_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove member: this farm must have at least one owner")
            
    db.delete(target_assoc)
    db.commit()
    return

