import datetime
import hashlib
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.blood_bank import BloodBank
from app.schemas.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    # Use SHA-256 with salt for guaranteed cross-platform reliability without C-extension hiccups
    salt = "lifelink_2026_salt"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    # Support both token auth and demo fallback
    if not token:
        # Return demo patient user by default if not authenticated for seamless demo flow
        patient_user = db.query(User).filter(User.role == "PATIENT").first()
        return patient_user
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = str(payload.get("sub"))
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_patient(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Patient:
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    if not patient:
        # If user is admin or caregiver checking, return first available patient
        patient = db.query(Patient).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")
    return patient

def get_current_blood_bank(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BloodBank:
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    bb = db.query(BloodBank).filter(BloodBank.user_id == user.id).first()
    if not bb:
        # Fallback to ABC Blood Bank for demo
        bb = db.query(BloodBank).first()
        if not bb:
            raise HTTPException(status_code=404, detail="Blood bank not found")
    return bb
