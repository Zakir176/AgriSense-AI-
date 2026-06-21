from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertBase(BaseModel):
    batch_id: int
    type: str
    message: str
    severity: str
    acknowledged: Optional[bool] = False

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    acknowledged: Optional[bool] = None

class AlertResponse(AlertBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
