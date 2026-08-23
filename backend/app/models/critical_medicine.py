import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.session import Base

class CriticalMedicine(Base):
    __tablename__ = "critical_medicines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # e.g., "Albumin 20% (Human Albumin Infusion)"
    pharmacy_name = Column(String(150), nullable=False)  # e.g., "ABC Hospital Pharmacy"
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String(50), nullable=False)
    units_available = Column(Integer, default=12)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    category = Column(String(50), default="CRITICAL_INFUSION")
