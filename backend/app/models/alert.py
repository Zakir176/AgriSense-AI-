from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    type = Column(String, nullable=False)  # e.g., feed_drop, water_deviation, growth_low
    message = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # info | warning | critical
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    acknowledged = Column(Boolean, default=False)

    batch = relationship("Batch", back_populates="alerts")
