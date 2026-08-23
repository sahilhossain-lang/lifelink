from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.blood_bank import BloodBank
from app.schemas.schemas import UserRegister, UserLogin, Token, UserOut
from app.services.auth_service import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    role = user_in.role.upper()
    user = User(
        name=user_in.name,
        email=user_in.email.lower(),
        phone=user_in.phone,
        password_hash=hash_password(user_in.password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    patient_id = None
    blood_bank_id = None

    if role == "PATIENT":
        patient = Patient(
            user_id=user.id,
            blood_group=user_in.blood_group or "B+",
            location=user_in.location or "Kolkata",
            date_of_birth=user_in.date_of_birth or "1998-05-14",
            emergency_contact=user_in.emergency_contact or user_in.phone
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        patient_id = patient.id
    elif role == "BLOOD_BANK":
        bb = BloodBank(
            user_id=user.id,
            name=user_in.name,
            address=user_in.location or "Kolkata Central, West Bengal",
            latitude=22.5726,
            longitude=88.3639,
            phone=user_in.phone or "+91 33 2222 1111",
            verified=True,
            source_name="Verified Regional Blood Centre"
        )
        db.add(bb)
        db.commit()
        db.refresh(bb)
        blood_bank_id = bb.id

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        patient_id=patient_id,
        blood_bank_id=blood_bank_id
    )

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    bb = db.query(BloodBank).filter(BloodBank.user_id == user.id).first()

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        patient_id=patient.id if patient else None,
        blood_bank_id=bb.id if bb else None
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
