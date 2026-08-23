import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.blood_bank import BloodBank
from app.models.blood_inventory import BloodInventory
from app.schemas.schemas import BloodBankOut, BloodSearchResult, InventoryUpdate, BloodInventoryItem
from app.services.blood_service import search_blood_availability, DEFAULT_LAT, DEFAULT_LNG

router = APIRouter(tags=["Blood & Blood Banks"])

@router.get("/blood/search", response_model=List[BloodSearchResult])
def search_blood(
    blood_group: str = Query("B+", description="Blood Group e.g. B+, O-, A+, etc."),
    component: str = Query("PRBC", description="Component e.g. PRBC, PLATELETS, FFP"),
    location: Optional[str] = Query("Kolkata", description="Location name"),
    lat: Optional[float] = Query(DEFAULT_LAT, description="User latitude"),
    lng: Optional[float] = Query(DEFAULT_LNG, description="User longitude"),
    db: Session = Depends(get_db)
):
    results = search_blood_availability(
        db=db,
        blood_group=blood_group,
        component=component,
        user_lat=lat or DEFAULT_LAT,
        user_lng=lng or DEFAULT_LNG
    )
    return results

@router.get("/blood-banks", response_model=List[BloodBankOut])
def get_all_blood_banks(db: Session = Depends(get_db)):
    banks = db.query(BloodBank).all()
    out = []
    for b in banks:
        inv_items = [
            BloodInventoryItem(
                blood_group=i.blood_group,
                component=i.component,
                units_available=i.units_available,
                last_updated=i.last_updated
            ) for i in b.inventory
        ]
        out.append(BloodBankOut(
            id=b.id,
            name=b.name,
            address=b.address,
            latitude=b.latitude,
            longitude=b.longitude,
            phone=b.phone,
            verified=b.verified,
            source_name=b.source_name,
            inventory=inv_items
        ))
    return out

@router.get("/blood-banks/{id}", response_model=BloodBankOut)
def get_blood_bank_by_id(id: int, db: Session = Depends(get_db)):
    b = db.query(BloodBank).filter(BloodBank.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Blood bank not found")
    inv_items = [
        BloodInventoryItem(
            blood_group=i.blood_group,
            component=i.component,
            units_available=i.units_available,
            last_updated=i.last_updated
        ) for i in b.inventory
    ]
    return BloodBankOut(
        id=b.id,
        name=b.name,
        address=b.address,
        latitude=b.latitude,
        longitude=b.longitude,
        phone=b.phone,
        verified=b.verified,
        source_name=b.source_name,
        inventory=inv_items
    )

@router.put("/blood-banks/{id}/inventory")
def update_blood_inventory(
    id: int,
    inv_in: InventoryUpdate,
    db: Session = Depends(get_db)
):
    b = db.query(BloodBank).filter(BloodBank.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Blood bank not found")
    
    norm_group = inv_in.blood_group.strip().upper()
    norm_comp = inv_in.component.strip().upper()
    
    item = db.query(BloodInventory).filter(
        BloodInventory.blood_bank_id == id,
        BloodInventory.blood_group == norm_group,
        BloodInventory.component == norm_comp
    ).first()

    if item:
        item.units_available = max(0, inv_in.units_available)
        item.last_updated = datetime.datetime.utcnow()
    else:
        item = BloodInventory(
            blood_bank_id=id,
            blood_group=norm_group,
            component=norm_comp,
            units_available=max(0, inv_in.units_available),
            last_updated=datetime.datetime.utcnow()
        )
        db.add(item)
    
    db.commit()
    db.refresh(item)
    return {"message": "Inventory updated successfully", "blood_group": norm_group, "units_available": item.units_available}
