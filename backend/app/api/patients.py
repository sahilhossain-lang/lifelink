from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.patient import Patient
from app.schemas.schemas import PatientOut, PatientCreate
from app.services.auth_service import get_current_user, get_current_patient

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/me", response_model=PatientOut)
def get_my_patient_profile(patient: Patient = Depends(get_current_patient)):
    return PatientOut(
        id=patient.id,
        user_id=patient.user_id,
        date_of_birth=patient.date_of_birth,
        blood_group=patient.blood_group,
        location=patient.location,
        emergency_contact=patient.emergency_contact,
        condition_diagnosis=patient.condition_diagnosis,
        created_at=patient.created_at,
        name=patient.user.name if patient.user else "Srijan",
        email=patient.user.email if patient.user else "srijan@lifelink.org"
    )

@router.put("/me", response_model=PatientOut)
def update_patient_profile(
    patient_in: PatientCreate,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    if patient_in.blood_group:
        patient.blood_group = patient_in.blood_group
    if patient_in.location:
        patient.location = patient_in.location
    if patient_in.date_of_birth:
        patient.date_of_birth = patient_in.date_of_birth
    if patient_in.emergency_contact:
        patient.emergency_contact = patient_in.emergency_contact
    if patient_in.condition_diagnosis:
        patient.condition_diagnosis = patient_in.condition_diagnosis
    
    db.commit()
    db.refresh(patient)
    return PatientOut(
        id=patient.id,
        user_id=patient.user_id,
        date_of_birth=patient.date_of_birth,
        blood_group=patient.blood_group,
        location=patient.location,
        emergency_contact=patient.emergency_contact,
        condition_diagnosis=patient.condition_diagnosis,
        created_at=patient.created_at,
        name=patient.user.name if patient.user else "Srijan",
        email=patient.user.email if patient.user else "srijan@lifelink.org"
    )
