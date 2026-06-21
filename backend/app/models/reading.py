from sqlalchemy import Column, Integer, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class FeedWaterReading(Base):
    __tablename__ = "feed_water_readings"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    date = Column(Date, nullable=False)
    feed_kg = Column(Float, nullable=False)
    water_litres = Column(Float, nullable=False)
    flagged_abnormal = Column(Boolean, default=False)

    batch = relationship("Batch", back_populates="readings")
