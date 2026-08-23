import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.reservation import BloodReservation
from app.models.blood_bank import BloodBank
from app.models.blood_inventory import BloodInventory
from app.models.patient import Patient
from app.models.user import User
from app.schemas.schemas import ReservationCreate, ReservationOut, ReservationStatusUpdate
from app.services.auth_service import get_current_user, get_current_patient
from app.services.notification_service import dispatch_notification

router = APIRouter(prefix="/reservations", tags=["Blood Reservations"])

@router.post("", response_model=ReservationOut)
def create_reservation(
    res_in: ReservationCreate,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    bb = db.query(BloodBank).filter(BloodBank.id == res_in.blood_bank_id).first()
    if not bb:
        raise HTTPException(status_code=404, detail="Selected blood bank not found")

    reservation = BloodReservation(
        patient_id=patient.id,
        blood_bank_id=res_in.blood_bank_id,
        blood_group=res_in.blood_group.upper(),
        component=res_in.component.upper(),
        units=res_in.units,
        required_date=res_in.required_date,
        status="PENDING",
        hospital_name=res_in.hospital_name,
        patient_notes=res_in.patient_notes
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    # Dispatch notification to patient & caregivers
    dispatch_notification(
        db=db,
        user_id=patient.user_id,
        title="Blood Reservation Requested (PENDING)",
        message=f"Requested {res_in.units} unit(s) of {res_in.blood_group} {res_in.component} from {bb.name} for {res_in.required_date}.",
        notif_type="RESERVATION",
        patient_id=patient.id
    )

    # Also notify blood bank user if linked
    if bb.user_id:
        dispatch_notification(
            db=db,
            user_id=bb.user_id,
            title="New Blood Reservation Request",
            message=f"Patient {patient.user.name if patient.user else 'Srijan'} requested {res_in.units} unit(s) of {res_in.blood_group} {res_in.component}.",
            notif_type="RESERVATION"
        )

    return _to_reservation_out(reservation)

@router.get("", response_model=List[ReservationOut])
def get_reservations(
    blood_bank_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    query = db.query(BloodReservation)
    if blood_bank_id:
        query = query.filter(BloodReservation.blood_bank_id == blood_bank_id)
    else:
        # If no specific blood_bank_id filtered, show patient's or all if requested
        query = query.filter(BloodReservation.patient_id == patient.id)

    if status:
        query = query.filter(BloodReservation.status == status.upper())

    reservations = query.order_by(BloodReservation.created_at.desc()).all()
    return [_to_reservation_out(r) for r in reservations]

@router.get("/all-requests", response_model=List[ReservationOut])
def get_all_requests_for_blood_bank(
    blood_bank_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieve all reservations for blood bank manager dashboard"""
    query = db.query(BloodReservation)
    if blood_bank_id:
        query = query.filter(BloodReservation.blood_bank_id == blood_bank_id)
    reservations = query.order_by(BloodReservation.created_at.desc()).all()
    return [_to_reservation_out(r) for r in reservations]

@router.get("/{id}", response_model=ReservationOut)
def get_reservation_by_id(id: int, db: Session = Depends(get_db)):
    res = db.query(BloodReservation).filter(BloodReservation.id == id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return _to_reservation_out(res)

@router.patch("/{id}", response_model=ReservationOut)
def update_reservation_status(
    id: int,
    status_update: ReservationStatusUpdate,
    db: Session = Depends(get_db)
):
    res = db.query(BloodReservation).filter(BloodReservation.id == id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    new_status = status_update.status.upper()
    res.status = new_status
    res.updated_at = datetime.datetime.utcnow()

    # If ACCEPTED, decrement the inventory units
    if new_status == "ACCEPTED":
        inv = db.query(BloodInventory).filter(
            BloodInventory.blood_bank_id == res.blood_bank_id,
            BloodInventory.blood_group == res.blood_group,
            BloodInventory.component == res.component
        ).first()
        if inv and inv.units_available >= res.units:
            inv.units_available -= res.units
            inv.last_updated = datetime.datetime.utcnow()

        # Send push notification to patient & caregiver
        bb_name = res.blood_bank.name if res.blood_bank else "ABC Blood Bank"
        dispatch_notification(
            db=db,
            user_id=res.patient.user_id,
            title="Blood Reservation Accepted!",
            message=f"Your blood reservation has been accepted by {bb_name}. {res.units} units of {res.blood_group} {res.component} are reserved for {res.required_date}.",
            notif_type="RESERVATION",
            patient_id=res.patient_id
        )

    elif new_status == "REJECTED":
        bb_name = res.blood_bank.name if res.blood_bank else "Blood Bank"
        dispatch_notification(
            db=db,
            user_id=res.patient.user_id,
            title="Blood Reservation Update",
            message=f"Your blood reservation request at {bb_name} could not be fulfilled. Please search nearby blood banks.",
            notif_type="RESERVATION",
            patient_id=res.patient_id
        )

    db.commit()
    db.refresh(res)
    return _to_reservation_out(res)

def _to_reservation_out(res: BloodReservation) -> ReservationOut:
    return ReservationOut(
        id=res.id,
        patient_id=res.patient_id,
        blood_bank_id=res.blood_bank_id,
        blood_bank_name=res.blood_bank.name if res.blood_bank else "ABC Blood Bank",
        blood_bank_phone=res.blood_bank.phone if res.blood_bank else "+91 33 2222 1111",
        blood_bank_address=res.blood_bank.address if res.blood_bank else "Kolkata",
        patient_name=res.patient.user.name if res.patient and res.patient.user else "Srijan",
        patient_phone=res.patient.user.phone if res.patient and res.patient.user else "+91 98300 12345",
        blood_group=res.blood_group,
        component=res.component,
        units=res.units,
        required_date=res.required_date,
        status=res.status,
        hospital_name=res.hospital_name,
        patient_notes=res.patient_notes,
        created_at=res.created_at,
        updated_at=res.updated_at
    )
