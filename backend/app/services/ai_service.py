import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.models.treatment import Treatment
from app.models.reservation import BloodReservation
from app.models.medicine import Medicine
from app.schemas.schemas import AIDailySummaryResponse, AICareItem

SAFETY_DISCLAIMER = (
    "LifeLink is an automated critical-care coordination and reminder platform. "
    "It organizes schedules and alerts but does NOT diagnose conditions, prescribe medications, "
    "alter chemotherapy protocols, or determine transfusion eligibility. Always consult your attending hematologist/oncologist."
)

def generate_ai_daily_summary(patient: Patient, db: Session) -> AIDailySummaryResponse:
    """
    Generate structured, safe AI Daily Care Summary (PDF Pages 9 & 13)
    Aggregates scheduled transfusions, blood reservation statuses, chemotherapy sessions,
    and daily medication reminders.
    """
    patient_name = patient.user.name if patient.user else "Patient"
    
    # Query patient's upcoming treatments
    treatments = db.query(Treatment).filter(
        Treatment.patient_id == patient.id,
        Treatment.status == "SCHEDULED"
    ).all()

    # Query reservations
    reservations = db.query(BloodReservation).filter(
        BloodReservation.patient_id == patient.id
    ).order_by(BloodReservation.created_at.desc()).all()

    # Query medicines
    medicines = db.query(Medicine).filter(
        Medicine.patient_id == patient.id
    ).all()

    care_tasks: List[AICareItem] = []
    summary_bullets: List[str] = []

    # 1. Transfusion & Reservation Status
    for t in treatments:
        if t.type.upper() == "TRANSFUSION":
            # Check matching reservation
            active_res = next((r for r in reservations if r.status in ["PENDING", "ACCEPTED"]), None)
            res_status_text = ""
            action_label = None
            action_type = None
            urgency = "HIGH"

            if active_res:
                if active_res.status == "ACCEPTED":
                    res_status_text = f"Blood reservation is confirmed ({active_res.units} units at {active_res.blood_bank.name if active_res.blood_bank else 'Blood Bank'})."
                    urgency = "MEDIUM"
                elif active_res.status == "PENDING":
                    res_status_text = f"Blood reservation is pending approval from {active_res.blood_bank.name if active_res.blood_bank else 'Blood Bank'}."
                    action_label = "View Status"
                    action_type = "RESERVATIONS"
            else:
                res_status_text = "No blood reservation found. Blood arrangement required."
                action_label = "Arrange Blood"
                action_type = "FIND_BLOOD"

            care_tasks.append(AICareItem(
                date=t.scheduled_date,
                title=f"Blood Transfusion ({t.blood_group or patient.blood_group} • {t.expected_units or 2} Units)",
                detail=f"Scheduled at {t.hospital}. {res_status_text}",
                urgency=urgency,
                action_label=action_label,
                action_type=action_type
            ))
            summary_bullets.append(f"{t.scheduled_date} — Transfusion scheduled; {res_status_text}")

        elif t.type.upper() == "CHEMOTHERAPY":
            care_tasks.append(AICareItem(
                date=t.scheduled_date,
                title=f"Chemotherapy Session ({t.cycle or 'Cycle Session'})",
                detail=f"Appointment at {t.hospital} at {t.appointment_time or '10:00 AM'}. Notes: {t.hospital_provided_notes or 'Standard pre-medication regimen'}",
                urgency="HIGH",
                action_label="View Protocol",
                action_type="TREATMENTS"
            ))
            summary_bullets.append(f"{t.scheduled_date} — Chemotherapy appointment at {t.appointment_time or '10:00 AM'}.")

    # 2. Daily Medicine Reminders
    for med in medicines:
        care_tasks.append(AICareItem(
            date="Today",
            title=f"Medicine: {med.name} ({med.dosage})",
            detail=f"{med.frequency} at {med.reminder_time}. {med.instructions or ''}",
            urgency="NORMAL",
            action_label="Take Dose",
            action_type="MEDICINES"
        ))
        summary_bullets.append(f"Today — {med.name} reminder at {med.reminder_time}.")

    # Compile the conversational AI summary (matching PDF Page 9 format)
    bullet_text = "\n".join([f"• {b}" for b in summary_bullets]) if summary_bullets else "• No pending critical care tasks scheduled."
    
    ai_summary_text = (
        f"Good morning {patient_name}!\n\n"
        f"You have {len(care_tasks)} important care tasks:\n"
        f"{bullet_text}\n\n"
        f"Please check your reservation status and medicine stock before the scheduled dates."
    )

    return AIDailySummaryResponse(
        greeting=f"Good morning, {patient_name}",
        patient_name=patient_name,
        total_care_tasks=len(care_tasks),
        ai_summary_text=ai_summary_text,
        care_tasks=care_tasks,
        safety_disclaimer=SAFETY_DISCLAIMER
    )
