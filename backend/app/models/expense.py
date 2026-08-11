from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    category = Column(String, nullable=False)  # feed | medication | equipment | labour | other
    description = Column(String, nullable=True)
    amount_zmw = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    batch = relationship("Batch", back_populates="expenses")
