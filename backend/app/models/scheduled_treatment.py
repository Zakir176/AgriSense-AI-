from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ScheduledTreatment(Base):
    __tablename__ = "scheduled_treatments"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    title = Column(String, nullable=False)                    # e.g. "Gumboro Dose 2"
    treatment_type = Column(String, nullable=False)           # "vaccine" | "medication" | "supplement"
    scheduled_date = Column(Date, nullable=False, index=True)
    dosage = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    status = Column(String, default="pending")                # "pending" | "completed" | "skipped"
    completed_date = Column(Date, nullable=True)
    remind_at = Column(DateTime, nullable=True)               # Optional reminder datetime
    prescribed_by = Column(String, nullable=True)             # e.g. "Dr. Sarah Jenkins (Veterinarian)"
    administered_by = Column(String, nullable=True)            # e.g. "Evans Kabwe (Farmhand)"
    digital_signature = Column(String, nullable=True)         # Verification hash / sign-off string
    reminder_channel = Column(String, default="browser")      # "browser" | "sms" | "both"
    phone_number = Column(String, nullable=True)              # Optional phone number for SMS reminders

    batch = relationship("Batch", back_populates="scheduled_treatments")
