from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

class InventoryAdjustmentBase(BaseModel):
    date: date
    adjustment_type: str = Field(..., max_length=50)  # mortality | sale | cull | addition | correction
    quantity_delta: int
    notes: Optional[str] = Field(None, max_length=1000)
    unit_price_zmw: Optional[float] = None
    buyer_name: Optional[str] = Field(None, max_length=200)
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
