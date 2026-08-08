from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base

class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    adjustment_type = Column(String, nullable=False)  # mortality | sale | cull | addition | correction
    quantity_delta = Column(Integer, nullable=False)  # negative for reduction, positive for addition
    source = Column(String, default="manual_entry")   # daily_reading | manual_entry
    reference_id = Column(Integer, nullable=True)     # e.g. reading_id if auto-created
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    batch = relationship("Batch", back_populates="inventory_adjustments")
