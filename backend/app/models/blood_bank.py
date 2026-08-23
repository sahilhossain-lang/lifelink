import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class BloodBank(Base):
    __tablename__ = "blood_banks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(150), nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String(50), nullable=False)
    verified = Column(Boolean, default=True)
    source_name = Column(String(100), default="Govt. Blood Portal / Verified Partner")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="blood_bank")
    inventory = relationship("BloodInventory", back_populates="blood_bank", cascade="all, delete-orphan")
    reservations = relationship("BloodReservation", back_populates="blood_bank", cascade="all, delete-orphan")
