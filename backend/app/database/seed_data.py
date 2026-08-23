import datetime
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine, Base
from app.models import (
    User, Patient, BloodBank, BloodInventory, BloodReservation,
    Treatment, Medicine, Caregiver, Notification, CriticalMedicine
)
from app.services.auth_service import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "srijan@lifelink.org").first():
            print("Database already seeded with LifeLink demo data.")
            return

        print("Seeding database with LifeLink demo data (PDF specifications)...")

        # 1. Create Patient User: Srijan
        patient_user = User(
            name="Srijan",
            email="srijan@lifelink.org",
            phone="+91 98300 12345",
            password_hash=hash_password("patient123"),
            role="PATIENT",
            created_at=datetime.datetime.utcnow()
        )
        db.add(patient_user)
        db.commit()
        db.refresh(patient_user)

        # Create Patient Profile (Thalassemia Major, B+)
        patient = Patient(
            user_id=patient_user.id,
            date_of_birth="1998-05-14",
            blood_group="B+",
            location="Kolkata, West Bengal",
            emergency_contact="+91 98311 88990",
            condition_diagnosis="Thalassemia Major (Transfusion Dependent)",
            created_at=datetime.datetime.utcnow()
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # 2. Create Blood Bank User & Blood Bank: ABC Blood Bank (PDF Page 10)
        bb_user = User(
            name="ABC Blood Bank Officer",
            email="manager@abcbloodbank.org",
            phone="+91 33 2223 4567",
            password_hash=hash_password("bloodbank123"),
            role="BLOOD_BANK",
            created_at=datetime.datetime.utcnow()
        )
        db.add(bb_user)
        db.commit()
        db.refresh(bb_user)

        abc_blood_bank = BloodBank(
            user_id=bb_user.id,
            name="ABC Blood Bank & Research Centre",
            address="14/1 Park Street, Central Kolkata - 700016",
            latitude=22.5510,
            longitude=88.3520,
            phone="+91 33 2223 4567",
            verified=True,
            source_name="State Blood Transfusion Council (SBTC) Verified",
            created_at=datetime.datetime.utcnow()
        )
        db.add(abc_blood_bank)

        # Additional Blood Banks in Kolkata with realistic coordinates
        city_blood_bank = BloodBank(
            name="City Lifeline Regional Blood Centre",
            address="88 College Street, College Square, Kolkata - 700073",
            latitude=22.5744,
            longitude=88.3639,
            phone="+91 33 2241 9000",
            verified=True,
            source_name="NACO National Blood Grid",
            created_at=datetime.datetime.utcnow()
        )
        db.add(city_blood_bank)

        apex_blood_bank = BloodBank(
            name="Apex Red Cross Blood Bank",
            address="Sector 1, Salt Lake City, Kolkata - 700064",
            latitude=22.5850,
            longitude=88.4100,
            phone="+91 33 2334 1122",
            verified=True,
            source_name="Indian Red Cross Society",
            created_at=datetime.datetime.utcnow()
        )
        db.add(apex_blood_bank)

        apollo_blood_bank = BloodBank(
            name="Apollo Gleneagles Blood Centre",
            address="58 Canal Circular Road, Kadapara, Kolkata - 700054",
            latitude=22.5700,
            longitude=88.4000,
            phone="+91 33 2320 3040",
            verified=True,
            source_name="NABH Accredited Hospital Blood Bank",
            created_at=datetime.datetime.utcnow()
        )
        db.add(apollo_blood_bank)

        db.commit()
        db.refresh(abc_blood_bank)
        db.refresh(city_blood_bank)
        db.refresh(apex_blood_bank)
        db.refresh(apollo_blood_bank)

        # 3. Seed Blood Inventory (PDF Page 10 & 19 specifications)
        # ABC Blood Bank:
        # O+ PRBC -> 10, O- PRBC -> 2, A+ PRBC -> 8, B+ PRBC -> 5, B- PRBC -> 1, AB+ PRBC -> 4
        abc_inventories = [
            ("O+", "PRBC", 10),
            ("O-", "PRBC", 2),
            ("A+", "PRBC", 8),
            ("A-", "PRBC", 3),
            ("B+", "PRBC", 5),
            ("B-", "PRBC", 1),
            ("AB+", "PRBC", 4),
            ("AB-", "PRBC", 2),
            ("B+", "PLATELETS", 12),
            ("B+", "FFP", 7),
            ("O+", "PLATELETS", 15),
            ("A+", "FFP", 6),
        ]
        for bg, comp, units in abc_inventories:
            db.add(BloodInventory(
                blood_bank_id=abc_blood_bank.id,
                blood_group=bg,
                component=comp,
                units_available=units,
                last_updated=datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
            ))

        # City Blood Bank inventory
        city_inventories = [
            ("B+", "PRBC", 8), ("O+", "PRBC", 14), ("A+", "PRBC", 4),
            ("B+", "PLATELETS", 9), ("AB+", "PRBC", 3)
        ]
        for bg, comp, units in city_inventories:
            db.add(BloodInventory(
                blood_bank_id=city_blood_bank.id,
                blood_group=bg,
                component=comp,
                units_available=units,
                last_updated=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            ))

        # Apex Blood Bank inventory
        apex_inventories = [
            ("B+", "PRBC", 3), ("O+", "PRBC", 9), ("A+", "PRBC", 6),
            ("B-", "PRBC", 4), ("AB+", "PRBC", 2)
        ]
        for bg, comp, units in apex_inventories:
            db.add(BloodInventory(
                blood_bank_id=apex_blood_bank.id,
                blood_group=bg,
                component=comp,
                units_available=units,
                last_updated=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
            ))

        # Apollo Blood Bank inventory
        apollo_inventories = [
            ("B+", "PRBC", 12), ("O-", "PRBC", 4), ("A+", "PRBC", 10),
            ("B+", "PLATELETS", 20), ("AB-", "PRBC", 1)
        ]
        for bg, comp, units in apollo_inventories:
            db.add(BloodInventory(
                blood_bank_id=apollo_blood_bank.id,
                blood_group=bg,
                component=comp,
                units_available=units,
                last_updated=datetime.datetime.utcnow() - datetime.timedelta(minutes=45)
            ))

        db.commit()

        # 4. Caregiver User & Link (PDF Page 8)
        caregiver_user = User(
            name="Anita (Caregiver)",
            email="anita.caregiver@lifelink.org",
            phone="+91 98311 88990",
            password_hash=hash_password("caregiver123"),
            role="CAREGIVER",
            created_at=datetime.datetime.utcnow()
        )
        db.add(caregiver_user)
        db.commit()
        db.refresh(caregiver_user)

        caregiver = Caregiver(
            patient_id=patient.id,
            user_id=caregiver_user.id,
            caregiver_name="Anita Roy",
            relationship_type="Mother & Primary Caregiver",
            email="anita.caregiver@lifelink.org",
            phone="+91 98311 88990",
            notifications_enabled=True,
            status="ACCEPTED"
        )
        db.add(caregiver)
        db.commit()

        # 5. Treatments (PDF Pages 7-8)
        # Transfusion: 05 September, B+ • 2 Units, Repeat every 21 days
        transfusion_treatment = Treatment(
            patient_id=patient.id,
            type="TRANSFUSION",
            hospital="Calcutta Medical Research Institute (CMRI)",
            scheduled_date="05 September 2026",
            appointment_time="10:30 AM",
            notes="Regular 21-day packed red blood cell transfusion cycle. Target Hb: >10 g/dL.",
            status="SCHEDULED",
            blood_group="B+",
            component="PRBC",
            expected_units=2,
            repeat_interval_days=21
        )
        db.add(transfusion_treatment)

        # Chemotherapy appointment (PDF Page 8)
        chemo_treatment = Treatment(
            patient_id=patient.id,
            type="CHEMOTHERAPY",
            hospital="Tata Medical Center",
            scheduled_date="12 September 2026",
            appointment_time="10:00 AM",
            cycle="Cycle 3 of 6",
            hospital_provided_notes="Pre-infusion antiemetic hydration protocol recommended 30 mins prior.",
            status="SCHEDULED"
        )
        db.add(chemo_treatment)
        db.commit()

        # 6. Medicines (PDF Page 8)
        # Deferasirox 500mg (Iron chelation): Initial 30, 2/day, started 5 days ago -> remaining 20
        five_days_ago = (datetime.date.today() - datetime.timedelta(days=5)).isoformat()
        med1 = Medicine(
            patient_id=patient.id,
            name="Deferasirox (Iron Chelation)",
            dosage="500 mg",
            frequency="2 tablets/day",
            daily_units=2.0,
            initial_quantity=30,
            start_date=five_days_ago,
            remaining_quantity=20,
            reminder_time="08:00 PM",
            instructions="Disperse in water or orange juice on an empty stomach 30 mins before food."
        )
        db.add(med1)

        # Hydroxyurea 500mg
        ten_days_ago = (datetime.date.today() - datetime.timedelta(days=10)).isoformat()
        med2 = Medicine(
            patient_id=patient.id,
            name="Hydroxyurea",
            dosage="500 mg",
            frequency="1 capsule/day",
            daily_units=1.0,
            initial_quantity=30,
            start_date=ten_days_ago,
            remaining_quantity=20,
            reminder_time="09:00 AM",
            instructions="Take in morning with a full glass of water. Wear gloves if handling open capsules."
        )
        db.add(med2)

        # Folic Acid 5mg
        two_days_ago = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
        med3 = Medicine(
            patient_id=patient.id,
            name="Folic Acid",
            dosage="5 mg",
            frequency="1 tablet/day",
            daily_units=1.0,
            initial_quantity=30,
            start_date=two_days_ago,
            remaining_quantity=28,
            reminder_time="01:00 PM",
            instructions="Take after lunch to support erythropoiesis."
        )
        db.add(med3)
        db.commit()

        # 7. Critical Medicines / Albumin (PDF Page 8 Section 12)
        alb1 = CriticalMedicine(
            name="Albumin 20% (Human Albumin Infusion 100ml)",
            pharmacy_name="ABC Hospital Pharmacy",
            address="14/1 Park Street, Kolkata",
            latitude=22.5510,
            longitude=88.3520,
            phone="+91 33 2223 4568",
            units_available=12,
            last_updated=datetime.datetime.utcnow() - datetime.timedelta(minutes=30),
            category="CRITICAL_INFUSION"
        )
        db.add(alb1)

        alb2 = CriticalMedicine(
            name="Albumin 20% (Human Albumin Infusion 100ml)",
            pharmacy_name="Medica Superspecialty Pharmacy",
            address="127 Mukundapur, EM Bypass, Kolkata",
            latitude=22.4988,
            longitude=88.3975,
            phone="+91 33 6652 0000",
            units_available=8,
            last_updated=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
            category="CRITICAL_INFUSION"
        )
        db.add(alb2)
        db.commit()

        # 8. Initial Notifications (PDF Page 8, 9)
        db.add(Notification(
            user_id=patient_user.id,
            title="Transfusion Cycle Approaching (7-day reminder)",
            message="Your next blood transfusion is scheduled on 05 September at CMRI. Please ensure 2 units of B+ PRBC are arranged.",
            type="REMINDER",
            is_read=False,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=4)
        ))
        db.add(Notification(
            user_id=patient_user.id,
            title="Evening Medicine Reminder",
            message="Time to take Deferasirox 500mg (2 tablets) with liquid at 08:00 PM.",
            type="REMINDER",
            is_read=False,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        ))

        # Admin user
        admin_user = User(
            name="System Admin",
            email="admin@lifelink.org",
            phone="+91 33 0000 0000",
            password_hash=hash_password("admin123"),
            role="ADMIN",
            created_at=datetime.datetime.utcnow()
        )
        db.add(admin_user)

        db.commit()
        print("LifeLink seed data inserted successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
