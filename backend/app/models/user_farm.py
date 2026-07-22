from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base

class UserFarmAssociation(Base):
    __tablename__ = "user_farm_associations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False, default="farmhand")  # owner | veterinarian | farmhand | data_analyst

    # Define relationships
    user = relationship("User", back_populates="user_farms")
    farm = relationship("Farm", back_populates="user_farms")

    __table_args__ = (
        UniqueConstraint("user_id", "farm_id", name="uq_user_farm"),
    )
