import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    name = Column(String(150), nullable=False)
    dosage = Column(String(50), nullable=False)  # e.g., "500 mg"
    frequency = Column(String(50), nullable=False)  # e.g., "2 tablets/day", "Once daily", "Twice daily"
    daily_units = Column(Float, nullable=False, default=1.0)  # Numerical daily rate for stock calculation
    initial_quantity = Column(Integer, nullable=False, default=30)
    start_date = Column(String(50), nullable=False)  # "2026-08-19"
    end_date = Column(String(50), nullable=True)
    remaining_quantity = Column(Integer, nullable=False, default=30)
    reminder_time = Column(String(20), nullable=False, default="08:00 PM")
    instructions = Column(String(255), nullable=True, default="Take after dinner with full glass of water")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="medicines")
