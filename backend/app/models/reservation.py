import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class BloodReservation(Base):
    __tablename__ = "blood_reservations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    blood_bank_id = Column(Integer, ForeignKey("blood_banks.id"), nullable=False)
    blood_group = Column(String(10), nullable=False)
    component = Column(String(30), nullable=False, default="PRBC")
    units = Column(Integer, nullable=False, default=1)
    required_date = Column(String(50), nullable=False)  # e.g., "2026-09-05" or "05 September 2026"
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING, ACCEPTED, REJECTED, CANCELLED, COMPLETED
    hospital_name = Column(String(150), nullable=True)
    patient_notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="reservations")
    blood_bank = relationship("BloodBank", back_populates="reservations")
