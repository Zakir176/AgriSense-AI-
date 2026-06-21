from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    bird_count = Column(Integer, nullable=False)
    breed = Column(String, nullable=False)
    status = Column(String, default="active")  # active | archived

    farm = relationship("Farm", back_populates="batches")
    readings = relationship("FeedWaterReading", back_populates="batch", cascade="all, delete-orphan")
    growth_samples = relationship("GrowthSample", back_populates="batch", cascade="all, delete-orphan")
    medications = relationship("MedicationEntry", back_populates="batch", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="batch", cascade="all, delete-orphan")
    media_clips = relationship("MediaClip", back_populates="batch", cascade="all, delete-orphan")
