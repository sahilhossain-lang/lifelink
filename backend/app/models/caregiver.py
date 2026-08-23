import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship as sa_relationship
from app.database.session import Base

class Caregiver(Base):
    __tablename__ = "caregivers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Linked registered caregiver user
    caregiver_name = Column(String(100), nullable=False)
    relationship_type = Column("relationship", String(50), nullable=False)  # e.g., "Mother", "Spouse"
    email = Column(String(150), nullable=True)
    phone = Column(String(30), nullable=False)
    notifications_enabled = Column(Boolean, default=True)
    status = Column(String(20), default="ACCEPTED")  # PENDING, ACCEPTED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    patient = sa_relationship("Patient", back_populates="caregivers")

