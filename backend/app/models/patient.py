import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    date_of_birth = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=False)  # e.g., B+, O+, A+, AB-
    location = Column(String(100), default="Kolkata")
    emergency_contact = Column(String(50), nullable=True)
    condition_diagnosis = Column(String(100), default="Thalassemia Major")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    reservations = relationship("BloodReservation", back_populates="patient", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="patient", cascade="all, delete-orphan")
    medicines = relationship("Medicine", back_populates="patient", cascade="all, delete-orphan")
    caregivers = relationship("Caregiver", back_populates="patient", cascade="all, delete-orphan")
