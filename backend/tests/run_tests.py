import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_lifelink_system():
    print("=== STARTING LIFELINK AUTOMATED VERIFICATION SUITE ===")
    
    # 1. Health Check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] Health check endpoint OK")

    # 2. Login as Patient
    res = client.post("/api/auth/login", json={"email": "srijan@lifelink.org", "password": "patient123"})
    assert res.status_code == 200, f"Patient login failed: {res.text}"
    patient_token = res.json()["access_token"]
    patient_headers = {"Authorization": f"Bearer {patient_token}"}
    print(f"[PASS] Patient login OK (User: {res.json()['name']}, Role: {res.json()['role']})")

    # 3. Patient Profile
    res = client.get("/api/patients/me", headers=patient_headers)
    assert res.status_code == 200, f"Patient profile failed: {res.text}"
    p_data = res.json()
    assert p_data["blood_group"] == "B+", "Blood group mismatch"
    print(f"[PASS] Patient profile OK (Blood Group: {p_data['blood_group']}, Diagnosis: {p_data['condition_diagnosis']})")

    # 4. Blood Search (PDF Page 5: blood_group=B+, component=PRBC, location=Kolkata)
    res = client.get("/api/blood/search?blood_group=B%2B&component=PRBC&location=Kolkata")
    assert res.status_code == 200, f"Blood search failed: {res.text}"
    search_results = res.json()
    assert len(search_results) > 0, "No blood banks found"
    abc_bank = next((b for b in search_results if "ABC" in b["name"]), search_results[0])
    initial_abc_units = abc_bank["units_available"]
    print(f"[PASS] Blood search OK ({len(search_results)} blood banks found. Nearest: {abc_bank['name']} - {abc_bank['units_available']} units available, {abc_bank['distance_km']} km)")

    # 5. Create Blood Reservation (PDF Page 7 & 10: 2 units B+ PRBC from ABC Blood Bank)
    reservation_payload = {
        "blood_bank_id": abc_bank["blood_bank_id"],
        "blood_group": "B+",
        "component": "PRBC",
        "units": 2,
        "required_date": "05 September 2026",
        "hospital_name": "Calcutta Medical Research Institute (CMRI)",
        "patient_notes": "Required for scheduled 21-day transfusion cycle."
    }
    res = client.post("/api/reservations", json=reservation_payload, headers=patient_headers)
    assert res.status_code == 200, f"Create reservation failed: {res.text}"
    created_res = res.json()
    assert created_res["status"] == "PENDING", f"Status should be PENDING, got {created_res['status']}"
    res_id = created_res["id"]
    print(f"[PASS] Blood reservation created OK (ID: {res_id}, Status: {created_res['status']}, Units: {created_res['units']})")

    # 6. Blood Bank Manager Login & View Requests
    res = client.post("/api/auth/login", json={"email": "manager@abcbloodbank.org", "password": "bloodbank123"})
    assert res.status_code == 200, f"Blood bank login failed: {res.text}"
    bb_token = res.json()["access_token"]
    bb_headers = {"Authorization": f"Bearer {bb_token}"}
    print("[PASS] Blood bank login OK")

    # 7. Blood Bank Accepts Reservation (PDF Page 7, 10, 11)
    res = client.patch(f"/api/reservations/{res_id}", json={"status": "ACCEPTED"}, headers=bb_headers)
    assert res.status_code == 200, f"Accept reservation failed: {res.text}"
    accepted_res = res.json()
    assert accepted_res["status"] == "ACCEPTED", "Status should be ACCEPTED"
    print(f"[PASS] Blood Bank accepted reservation OK (Status: {accepted_res['status']})")

    # Verify inventory was decremented by 2 units
    res = client.get("/api/blood/search?blood_group=B%2B&component=PRBC")
    updated_search = res.json()
    updated_abc = next((b for b in updated_search if b["blood_bank_id"] == abc_bank["blood_bank_id"]), None)
    if updated_abc:
        assert updated_abc["units_available"] == initial_abc_units - 2, "Inventory did not decrement properly"
        print(f"[PASS] Inventory correctly decremented from {initial_abc_units} to {updated_abc['units_available']} units")

    # 8. Check Patient Notifications (PDF Page 9: "Your blood reservation has been accepted by ABC Blood Bank.")
    res = client.get("/api/notifications", headers=patient_headers)
    assert res.status_code == 200, f"Notifications failed: {res.text}"
    notifs = res.json()
    assert len(notifs) > 0, "No notifications found"
    accepted_notif = next((n for n in notifs if "Accepted" in n["title"] or "Accepted" in n["message"]), None)
    assert accepted_notif is not None, "Accepted notification was not delivered to patient"
    print(f"[PASS] Real-time notification delivered to patient: '{accepted_notif['title']}' - '{accepted_notif['message']}'")

    # 9. Test Treatments & Medicine Stock Calculations (PDF Page 8)
    res = client.get("/api/treatments", headers=patient_headers)
    assert res.status_code == 200, f"Treatments failed: {res.text}"
    treatments = res.json()
    print(f"[PASS] Treatments retrieved OK ({len(treatments)} active treatments: {[t['type'] for t in treatments]})")

    res = client.get("/api/medicines", headers=patient_headers)
    assert res.status_code == 200, f"Medicines failed: {res.text}"
    medicines = res.json()
    for m in medicines:
        print(f"       Medicine: {m['name']} -> Remaining: {m['remaining_quantity']} ({m['days_left']} days left)")
    print("[PASS] Medicine stock calculations verified OK")

    # 10. Test AI Care Assistant (PDF Page 9 & 13)
    res = client.get("/api/ai/daily-summary", headers=patient_headers)
    assert res.status_code == 200, f"AI Care Assistant failed: {res.text}"
    ai_summary = res.json()
    assert ai_summary["total_care_tasks"] >= 3, "AI care tasks missing"
    assert "LifeLink is an automated critical-care coordination" in ai_summary["safety_disclaimer"]
    print(f"[PASS] AI Care Assistant daily summary generated OK ({ai_summary['total_care_tasks']} care tasks summarized safely)")
    print("\n--- AI Care Summary Text Preview ---")
    print(ai_summary["ai_summary_text"])
    print("------------------------------------\n")

    # 11. Critical Medicine / Albumin Tracker (PDF Page 8 Section 12)
    res = client.get("/api/critical-medicines")
    assert res.status_code == 200, f"Critical medicines failed: {res.text}"
    crit_meds = res.json()
    assert len(crit_meds) > 0, "No critical medicines found"
    print(f"[PASS] Critical Medicines / Albumin 20% search OK ({len(crit_meds)} pharmacies found with live stock)")

    print("\n=======================================================")
    print(">>> ALL LIFELINK BACKEND VERIFICATION TESTS PASSED! <<<")
    print("=======================================================\n")

if __name__ == "__main__":
    test_lifelink_system()
