from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.medicine import Medicine
from app.models.patient import Patient
from app.schemas.schemas import MedicineCreate, MedicineUpdate, MedicineOut
from app.services.auth_service import get_current_patient
from app.services.medicine_service import calculate_medicine_stock

router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.get("", response_model=List[MedicineOut])
def get_medicines(
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    medicines = db.query(Medicine).filter(Medicine.patient_id == patient.id).all()
    results = []
    for med in medicines:
        rem_qty, days_left = calculate_medicine_stock(med)
        results.append(MedicineOut(
            id=med.id,
            patient_id=med.patient_id,
            name=med.name,
            dosage=med.dosage,
            frequency=med.frequency,
            daily_units=med.daily_units,
            initial_quantity=med.initial_quantity,
            start_date=med.start_date,
            end_date=med.end_date,
            remaining_quantity=rem_qty,
            days_left=days_left,
            reminder_time=med.reminder_time,
            instructions=med.instructions,
            created_at=med.created_at
        ))
    return results

@router.post("", response_model=MedicineOut)
def create_medicine(
    med_in: MedicineCreate,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    med = Medicine(
        patient_id=patient.id,
        name=med_in.name,
        dosage=med_in.dosage,
        frequency=med_in.frequency,
        daily_units=med_in.daily_units,
        initial_quantity=med_in.initial_quantity,
        start_date=med_in.start_date,
        end_date=med_in.end_date,
        remaining_quantity=med_in.initial_quantity,
        reminder_time=med_in.reminder_time,
        instructions=med_in.instructions
    )
    db.add(med)
    db.commit()
    db.refresh(med)

    rem_qty, days_left = calculate_medicine_stock(med)
    return MedicineOut(
        id=med.id,
        patient_id=med.patient_id,
        name=med.name,
        dosage=med.dosage,
        frequency=med.frequency,
        daily_units=med.daily_units,
        initial_quantity=med.initial_quantity,
        start_date=med.start_date,
        end_date=med.end_date,
        remaining_quantity=rem_qty,
        days_left=days_left,
        reminder_time=med.reminder_time,
        instructions=med.instructions,
        created_at=med.created_at
    )

@router.patch("/{id}", response_model=MedicineOut)
def update_medicine(
    id: int,
    med_in: MedicineUpdate,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    med = db.query(Medicine).filter(Medicine.id == id, Medicine.patient_id == patient.id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")

    if med_in.name is not None:
        med.name = med_in.name
    if med_in.dosage is not None:
        med.dosage = med_in.dosage
    if med_in.frequency is not None:
        med.frequency = med_in.frequency
    if med_in.daily_units is not None:
        med.daily_units = med_in.daily_units
    if med_in.reminder_time is not None:
        med.reminder_time = med_in.reminder_time
    if med_in.instructions is not None:
        med.instructions = med_in.instructions
    if med_in.remaining_quantity is not None:
        med.remaining_quantity = med_in.remaining_quantity
        med.initial_quantity = med_in.remaining_quantity

    db.commit()
    db.refresh(med)

    rem_qty, days_left = calculate_medicine_stock(med)
    return MedicineOut(
        id=med.id,
        patient_id=med.patient_id,
        name=med.name,
        dosage=med.dosage,
        frequency=med.frequency,
        daily_units=med.daily_units,
        initial_quantity=med.initial_quantity,
        start_date=med.start_date,
        end_date=med.end_date,
        remaining_quantity=rem_qty,
        days_left=days_left,
        reminder_time=med.reminder_time,
        instructions=med.instructions,
        created_at=med.created_at
    )

@router.delete("/{id}")
def delete_medicine(
    id: int,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    med = db.query(Medicine).filter(Medicine.id == id, Medicine.patient_id == patient.id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(med)
    db.commit()
    return {"message": "Medicine removed successfully"}
