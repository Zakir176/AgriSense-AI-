from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ExpenseCreate(BaseModel):
    date: date
    category: str  # feed | medication | equipment | labour | other
    description: Optional[str] = None
    amount_zmw: float

class ExpenseResponse(ExpenseCreate):
    id: int
    batch_id: int
    created_at: datetime

    class Config:
        from_attributes = True
