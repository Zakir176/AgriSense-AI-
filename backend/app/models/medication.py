from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class MedicationEntry(Base):
    __tablename__ = "medication_entries"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    date = Column(Date, nullable=False)
    medicine_type = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    outcome_note = Column(String, nullable=True)

    batch = relationship("Batch", back_populates="medications")
