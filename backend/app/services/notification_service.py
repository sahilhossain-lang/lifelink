import datetime
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.caregiver import Caregiver

def dispatch_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notif_type: str = "RESERVATION",
    notify_caregivers: bool = True,
    patient_id: int = None
) -> Notification:
    """
    Create a notification for user, and automatically forward critical alerts to linked caregivers
    (PDF Page 8 & 9 Specification: Caregiver Mode & Push notifications)
    """
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type,
        is_read=False,
        created_at=datetime.datetime.utcnow()
    )
    db.add(notif)
    
    # Notify caregivers if linked
    if notify_caregivers and patient_id:
        caregivers = db.query(Caregiver).filter(
            Caregiver.patient_id == patient_id,
            Caregiver.notifications_enabled == True
        ).all()
        for cg in caregivers:
            if cg.user_id and cg.user_id != user_id:
                cg_notif = Notification(
                    user_id=cg.user_id,
                    title=f"[Caregiver Alert] {title}",
                    message=f"Patient Update: {message}",
                    type="CAREGIVER_ALERT",
                    is_read=False,
                    created_at=datetime.datetime.utcnow()
                )
                db.add(cg_notif)

    db.commit()
    db.refresh(notif)
    return notif
