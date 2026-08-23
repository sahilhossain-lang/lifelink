from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.patient import Patient
from app.schemas.schemas import AIDailySummaryResponse
from app.services.auth_service import get_current_patient
from app.services.ai_service import generate_ai_daily_summary

router = APIRouter(prefix="/ai", tags=["AI Care Assistant"])

@router.get("/daily-summary", response_model=AIDailySummaryResponse)
def get_daily_care_summary(
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Returns AI Daily Care Summary (PDF Page 9 & 13)
    Summarizes upcoming care tasks, transfusion/chemo schedules, medicine reminders,
    and reservation status while strictly adhering to safety rules.
    """
    return generate_ai_daily_summary(patient=patient, db=db)
