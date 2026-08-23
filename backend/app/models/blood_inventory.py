import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class BloodInventory(Base):
    __tablename__ = "blood_inventory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    blood_bank_id = Column(Integer, ForeignKey("blood_banks.id"), nullable=False)
    blood_group = Column(String(10), nullable=False)  # O+, O-, A+, A-, B+, B-, AB+, AB-
    component = Column(String(30), nullable=False, default="PRBC")  # PRBC, PLATELETS, FFP, WHOLE_BLOOD
    units_available = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    blood_bank = relationship("BloodBank", back_populates="inventory")
