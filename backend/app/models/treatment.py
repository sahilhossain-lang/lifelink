import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    type = Column(String(50), nullable=False)  # TRANSFUSION, CHEMOTHERAPY, OTHER
    hospital = Column(String(150), nullable=False)
    scheduled_date = Column(String(50), nullable=False)  # ISO string or "2026-09-05"
    appointment_time = Column(String(20), nullable=True, default="10:00 AM")
    notes = Column(String(500), nullable=True)
    status = Column(String(30), default="SCHEDULED")  # SCHEDULED, COMPLETED, CANCELLED
    
    # Specific fields for Transfusion tracker (PDF Page 7)
    blood_group = Column(String(10), nullable=True)
    component = Column(String(30), nullable=True, default="PRBC")
    expected_units = Column(Integer, nullable=True, default=2)
    repeat_interval_days = Column(Integer, nullable=True, default=21)
    
    # Specific fields for Chemotherapy tracker (PDF Page 8)
    cycle = Column(String(50), nullable=True, default="Cycle 3 of 6")
    hospital_provided_notes = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="treatments")
