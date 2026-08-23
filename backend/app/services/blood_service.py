import math
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.blood_bank import BloodBank
from app.models.blood_inventory import BloodInventory
from app.schemas.schemas import BloodSearchResult

# Kolkata center default coordinates
DEFAULT_LAT = 22.5726
DEFAULT_LNG = 88.3639

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two geo-coordinates using Haversine formula"""
    R = 6371.0  # Earth's radius in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def search_blood_availability(
    db: Session,
    blood_group: str,
    component: str = "PRBC",
    user_lat: float = DEFAULT_LAT,
    user_lng: float = DEFAULT_LNG,
    max_distance_km: float = 50.0
) -> List[BloodSearchResult]:
    """
    Search blood availability across blood banks, filtered by blood_group and component,
    sorted by distance (PDF Page 5 & 9).
    """
    # Normalize inputs
    norm_blood_group = blood_group.strip().upper()
    norm_component = component.strip().upper()
    
    blood_banks = db.query(BloodBank).all()
    results: List[BloodSearchResult] = []

    for bb in blood_banks:
        dist = calculate_haversine_distance(user_lat, user_lng, bb.latitude, bb.longitude)
        if dist > max_distance_km:
            continue
        
        # Check inventory for this blood group and component
        inv = db.query(BloodInventory).filter(
            BloodInventory.blood_bank_id == bb.id,
            BloodInventory.blood_group == norm_blood_group,
            BloodInventory.component == norm_component
        ).first()

        units = inv.units_available if inv else 0
        last_updated_str = (inv.last_updated.isoformat() if inv and inv.last_updated 
                            else "2026-08-23T20:30:00")

        results.append(BloodSearchResult(
            blood_bank_id=bb.id,
            name=bb.name,
            address=bb.address,
            phone=bb.phone,
            blood_group=norm_blood_group,
            component=norm_component,
            units_available=units,
            distance_km=dist,
            last_updated=last_updated_str,
            verified=bb.verified,
            source_name=bb.source_name
        ))

    # Sort results by distance ascending
    results.sort(key=lambda x: x.distance_km)
    return results
