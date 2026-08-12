from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

class InventoryAdjustmentBase(BaseModel):
    date: date
    adjustment_type: str  # mortality | sale | cull | addition | correction
    quantity_delta: int
    notes: Optional[str] = None
    unit_price_zmw: Optional[float] = None
    buyer_name: Optional[str] = None
    total_amount_zmw: Optional[float] = None

class InventoryAdjustmentCreate(InventoryAdjustmentBase):
    pass

class InventoryAdjustmentResponse(InventoryAdjustmentBase):
    id: int
    batch_id: int
    source: str
    reference_id: Optional[int] = None
    created_at: datetime
    unit_price_zmw: Optional[float] = None
    buyer_name: Optional[str] = None
    total_amount_zmw: Optional[float] = None

    class Config:
        from_attributes = True

class FlockInventorySummary(BaseModel):
    batch_id: int
    initial_bird_count: int
    total_mortality: int
    total_sales: int
    total_culls: int
    total_additions: int
    total_corrections: int
    current_live_count: int
    history: List[InventoryAdjustmentResponse]
