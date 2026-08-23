import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# Auth Schemas
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: str = "PATIENT"  # PATIENT, CAREGIVER, BLOOD_BANK, ADMIN
    # Optional patient profile fields if registering as patient
    blood_group: Optional[str] = "B+"
    location: Optional[str] = "Kolkata"
    date_of_birth: Optional[str] = None
    emergency_contact: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: str
    patient_id: Optional[int] = None
    blood_bank_id: Optional[int] = None

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Patient Schemas
class PatientCreate(BaseModel):
    date_of_birth: Optional[str] = None
    blood_group: str
    location: str = "Kolkata"
    emergency_contact: Optional[str] = None
    condition_diagnosis: Optional[str] = "Thalassemia Major"

class PatientOut(BaseModel):
    id: int
    user_id: int
    date_of_birth: Optional[str]
    blood_group: str
    location: str
    emergency_contact: Optional[str]
    condition_diagnosis: Optional[str]
    created_at: datetime.datetime
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

# Blood Inventory & Bank Schemas
class BloodInventoryItem(BaseModel):
    blood_group: str
    component: str = "PRBC"
    units_available: int
    last_updated: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class BloodBankOut(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    phone: str
    verified: bool
    source_name: str
    inventory: Optional[List[BloodInventoryItem]] = []

    class Config:
        from_attributes = True

class BloodSearchResult(BaseModel):
    blood_bank_id: int
    name: str
    address: str
    phone: str
    blood_group: str
    component: str
    units_available: int
    distance_km: float
    last_updated: str
    verified: bool
    source_name: str

class InventoryUpdate(BaseModel):
    blood_group: str
    component: str = "PRBC"
    units_available: int

# Blood Reservation Schemas
class ReservationCreate(BaseModel):
    blood_bank_id: int
    blood_group: str
    component: str = "PRBC"
    units: int = 1
    required_date: str
    hospital_name: Optional[str] = "Calcutta Medical Research Institute"
    patient_notes: Optional[str] = None

class ReservationStatusUpdate(BaseModel):
    status: str  # PENDING, ACCEPTED, REJECTED, CANCELLED, COMPLETED

class ReservationOut(BaseModel):
    id: int
    patient_id: int
    blood_bank_id: int
    blood_bank_name: Optional[str] = None
    blood_bank_phone: Optional[str] = None
    blood_bank_address: Optional[str] = None
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    blood_group: str
    component: str
    units: int
    required_date: str
    status: str
    hospital_name: Optional[str]
    patient_notes: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# Treatment Schemas
class TreatmentCreate(BaseModel):
    type: str  # TRANSFUSION, CHEMOTHERAPY, OTHER
    hospital: str
    scheduled_date: str
    appointment_time: Optional[str] = "10:00 AM"
    notes: Optional[str] = None
    blood_group: Optional[str] = "B+"
    component: Optional[str] = "PRBC"
    expected_units: Optional[int] = 2
    repeat_interval_days: Optional[int] = 21
    cycle: Optional[str] = None
    hospital_provided_notes: Optional[str] = None

class TreatmentOut(BaseModel):
    id: int
    patient_id: int
    type: str
    hospital: str
    scheduled_date: str
    appointment_time: Optional[str]
    notes: Optional[str]
    status: str
    blood_group: Optional[str]
    component: Optional[str]
    expected_units: Optional[int]
    repeat_interval_days: Optional[int]
    cycle: Optional[str]
    hospital_provided_notes: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Medicine Schemas
class MedicineCreate(BaseModel):
    name: str
    dosage: str
    frequency: str
    daily_units: float = 1.0
    initial_quantity: int = 30
    start_date: str
    end_date: Optional[str] = None
    reminder_time: str = "08:00 PM"
    instructions: Optional[str] = "Take after meal"

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    daily_units: Optional[float] = None
    remaining_quantity: Optional[int] = None
    reminder_time: Optional[str] = None
    instructions: Optional[str] = None

class MedicineOut(BaseModel):
    id: int
    patient_id: int
    name: str
    dosage: str
    frequency: str
    daily_units: float
    initial_quantity: int
    start_date: str
    end_date: Optional[str]
    remaining_quantity: int
    days_left: int
    reminder_time: str
    instructions: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Caregiver Schemas
class CaregiverCreate(BaseModel):
    caregiver_name: str
    relationship: str
    email: Optional[str] = None
    phone: str
    notifications_enabled: bool = True

class CaregiverOut(BaseModel):
    id: int
    patient_id: int
    caregiver_name: str
    relationship: str
    email: Optional[str]
    phone: str
    notifications_enabled: bool
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    scheduled_at: Optional[datetime.datetime]
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: bool

# Critical Medicine (Albumin) Schemas
class CriticalMedicineOut(BaseModel):
    id: int
    name: str
    pharmacy_name: str
    address: str
    latitude: float
    longitude: float
    phone: str
    units_available: int
    distance_km: Optional[float] = 0.0
    last_updated: datetime.datetime
    category: str

    class Config:
        from_attributes = True

# AI Care Assistant Schemas
class AICareItem(BaseModel):
    date: str
    title: str
    detail: str
    urgency: str  # HIGH, MEDIUM, NORMAL
    action_label: Optional[str] = None
    action_type: Optional[str] = None

class AIDailySummaryResponse(BaseModel):
    greeting: str
    patient_name: str
    total_care_tasks: int
    ai_summary_text: str
    care_tasks: List[AICareItem]
    safety_disclaimer: str
