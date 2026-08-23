from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.critical_medicine import CriticalMedicine
from app.schemas.schemas import CriticalMedicineOut
from app.services.blood_service import calculate_haversine_distance, DEFAULT_LAT, DEFAULT_LNG

router = APIRouter(prefix="/critical-medicines", tags=["Critical Medicines"])

@router.get("", response_model=List[CriticalMedicineOut])
def get_critical_medicines(
    search: Optional[str] = Query(None),
    lat: Optional[float] = Query(DEFAULT_LAT),
    lng: Optional[float] = Query(DEFAULT_LNG),
    db: Session = Depends(get_db)
):
    query = db.query(CriticalMedicine)
    if search:
        query = query.filter(CriticalMedicine.name.ilike(f"%{search}%"))
    
    meds = query.all()
    out = []
    user_lat = lat or DEFAULT_LAT
    user_lng = lng or DEFAULT_LNG

    for m in meds:
        dist = calculate_haversine_distance(user_lat, user_lng, m.latitude, m.longitude)
        out.append(CriticalMedicineOut(
            id=m.id,
            name=m.name,
            pharmacy_name=m.pharmacy_name,
            address=m.address,
            latitude=m.latitude,
            longitude=m.longitude,
            phone=m.phone,
            units_available=m.units_available,
            distance_km=dist,
            last_updated=m.last_updated,
            category=m.category
        ))
    
    out.sort(key=lambda x: x.distance_km)
    return out
