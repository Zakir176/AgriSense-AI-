from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class AudioConfig(Base):
    __tablename__ = "audio_configs"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Thresholds represent the sensitivity % required to trigger a warning/critical state
    cough_threshold_pct = Column(Float, default=80.0, nullable=False)
    chirp_threshold_pct = Column(Float, default=65.0, nullable=False)

    farm = relationship("Farm")
