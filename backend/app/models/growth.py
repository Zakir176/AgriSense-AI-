from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class GrowthSample(Base):
    __tablename__ = "growth_samples"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    avg_weight_g = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)

    batch = relationship("Batch", back_populates="growth_samples")
