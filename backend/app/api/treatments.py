from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.treatment import Treatment
from app.models.patient import Patient
from app.schemas.schemas import TreatmentCreate, TreatmentOut
from app.services.auth_service import get_current_patient

router = APIRouter(prefix="/treatments", tags=["Treatments"])

@router.get("", response_model=List[TreatmentOut])
def get_treatments(
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    treatments = db.query(Treatment).filter(
        Treatment.patient_id == patient.id
    ).order_by(Treatment.scheduled_date.asc()).all()
    return treatments

@router.post("", response_model=TreatmentOut)
def create_treatment(
    treatment_in: TreatmentCreate,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    treatment = Treatment(
        patient_id=patient.id,
        type=treatment_in.type.upper(),
        hospital=treatment_in.hospital,
        scheduled_date=treatment_in.scheduled_date,
        appointment_time=treatment_in.appointment_time or "10:00 AM",
        notes=treatment_in.notes,
        status="SCHEDULED",
        blood_group=treatment_in.blood_group or patient.blood_group,
        component=treatment_in.component or "PRBC",
        expected_units=treatment_in.expected_units or 2,
        repeat_interval_days=treatment_in.repeat_interval_days or 21,
        cycle=treatment_in.cycle,
        hospital_provided_notes=treatment_in.hospital_provided_notes
    )
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment

@router.delete("/{id}")
def delete_treatment(
    id: int,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    t = db.query(Treatment).filter(Treatment.id == id, Treatment.patient_id == patient.id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Treatment schedule not found")
    db.delete(t)
    db.commit()
    return {"message": "Treatment removed successfully"}
