from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.inventory import InventoryAdjustment
from ..models.batch import Batch
from ..models.auth import User
from ..schemas.inventory import InventoryAdjustmentCreate, InventoryAdjustmentResponse, FlockInventorySummary
from .auth import get_current_user, get_user_farm

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.post("/batch/{batch_id}", response_model=InventoryAdjustmentResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_adjustment(
    batch_id: int,
    adjustment: InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    assoc = get_user_farm(batch.farm_id, current_user, db)
    if assoc.role == "viewer":
        raise HTTPException(status_code=403, detail="Viewer role does not have permission to adjust inventory")

    # Normalize quantity_delta sign depending on type if needed
    delta = adjustment.quantity_delta
    adj_type = adjustment.adjustment_type.lower()
    if adj_type in ["mortality", "sale", "cull"] and delta > 0:
        delta = -delta
    elif adj_type == "addition" and delta < 0:
        delta = abs(delta)

    db_adj = InventoryAdjustment(
        batch_id=batch_id,
        date=adjustment.date,
        adjustment_type=adj_type,
        quantity_delta=delta,
        source="manual_entry",
        notes=adjustment.notes
    )

    db.add(db_adj)
    db.commit()
    db.refresh(db_adj)
    return db_adj

@router.get("/batch/{batch_id}", response_model=List[InventoryAdjustmentResponse])
def list_inventory_adjustments(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    get_user_farm(batch.farm_id, current_user, db)

    return db.query(InventoryAdjustment).filter(
        InventoryAdjustment.batch_id == batch_id
    ).order_by(InventoryAdjustment.date.desc(), InventoryAdjustment.created_at.desc()).all()

@router.get("/batch/{batch_id}/summary", response_model=FlockInventorySummary)
def get_inventory_summary(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    get_user_farm(batch.farm_id, current_user, db)

    adjustments = db.query(InventoryAdjustment).filter(
        InventoryAdjustment.batch_id == batch_id
    ).order_by(InventoryAdjustment.date.desc(), InventoryAdjustment.created_at.desc()).all()

    total_mortality = 0
    total_sales = 0
    total_culls = 0
    total_additions = 0
    total_corrections = 0
    net_delta = 0

    for adj in adjustments:
        net_delta += adj.quantity_delta
        atype = adj.adjustment_type.lower()
        if atype == "mortality":
            total_mortality += abs(adj.quantity_delta)
        elif atype == "sale":
            total_sales += abs(adj.quantity_delta)
        elif atype == "cull":
            total_culls += abs(adj.quantity_delta)
        elif atype == "addition":
            total_additions += abs(adj.quantity_delta)
        elif atype == "correction":
            total_corrections += adj.quantity_delta

    current_live = max(0, batch.bird_count + net_delta)

    return FlockInventorySummary(
        batch_id=batch_id,
        initial_bird_count=batch.bird_count,
        total_mortality=total_mortality,
        total_sales=total_sales,
        total_culls=total_culls,
        total_additions=total_additions,
        total_corrections=total_corrections,
        current_live_count=current_live,
        history=adjustments
    )
