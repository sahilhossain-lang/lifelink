from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.caregiver import Caregiver
from app.models.patient import Patient
from app.schemas.schemas import CaregiverCreate, CaregiverOut
from app.services.auth_service import get_current_patient

router = APIRouter(prefix="/caregivers", tags=["Caregivers"])

@router.get("", response_model=List[CaregiverOut])
def get_caregivers(
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    caregivers = db.query(Caregiver).filter(Caregiver.patient_id == patient.id).all()
    return [
        CaregiverOut(
            id=cg.id,
            patient_id=cg.patient_id,
            caregiver_name=cg.caregiver_name,
            relationship=cg.relationship_type,
            email=cg.email,
            phone=cg.phone,
            notifications_enabled=cg.notifications_enabled,
            status=cg.status,
            created_at=cg.created_at
        ) for cg in caregivers
    ]

@router.post("", response_model=CaregiverOut)
def add_caregiver(
    cg_in: CaregiverCreate,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    cg = Caregiver(
        patient_id=patient.id,
        caregiver_name=cg_in.caregiver_name,
        relationship_type=cg_in.relationship,
        email=cg_in.email,
        phone=cg_in.phone,
        notifications_enabled=cg_in.notifications_enabled,
        status="ACCEPTED"
    )
    db.add(cg)
    db.commit()
    db.refresh(cg)
    return CaregiverOut(
        id=cg.id,
        patient_id=cg.patient_id,
        caregiver_name=cg.caregiver_name,
        relationship=cg.relationship_type,
        email=cg.email,
        phone=cg.phone,
        notifications_enabled=cg.notifications_enabled,
        status=cg.status,
        created_at=cg.created_at
    )

@router.delete("/{id}")
def remove_caregiver(
    id: int,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    cg = db.query(Caregiver).filter(Caregiver.id == id, Caregiver.patient_id == patient.id).first()
    if not cg:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    db.delete(cg)
    db.commit()
    return {"message": "Caregiver unlinked successfully"}
