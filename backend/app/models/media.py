from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class MediaClip(Base):
    __tablename__ = "media_clips"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    file_url = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    batch = relationship("Batch", back_populates="media_clips")
    inference_result = relationship("InferenceResult", back_populates="media_clip", uselist=False, cascade="all, delete-orphan")

class InferenceResult(Base):
    __tablename__ = "inference_results"

    id = Column(Integer, primary_key=True, index=True)
    media_clip_id = Column(Integer, ForeignKey("media_clips.id"), nullable=False, unique=True)
    bird_count_est = Column(Integer, nullable=True)
    movement_score = Column(Float, nullable=True)
    low_activity_windows = Column(JSON, nullable=True)  # JSON representation of low activity ranges

    media_clip = relationship("MediaClip", back_populates="inference_result")
