import uuid
import requests

TURF_URL = "http://localhost:8001/api/v1"
BOOKING_URL = "http://localhost:8002/api/v1"
PAYMENT_URL = "http://localhost:8003/api/v1"
NOTIF_URL = "http://localhost:8004/api/v1"

def run_e2e_deployment_test():
    print("=" * 60)
    print("STARTING E2E CONTAINERIZED WORKFLOW TEST")
    print("=" * 60)

    # 1. Health Checks
    for name, port in [("Turf", 8001), ("Booking", 8002), ("Payment", 8003), ("Notification", 8004)]:
        res = requests.get(f"http://localhost:{port}/health")
        assert res.status_code == 200, f"{name} service healthcheck failed!"
        print(f"[OK] {name} Service is healthy (Port {port})")

    # 2. Step 1: Create Turf (Idempotent)
    idem_key_turf = str(uuid.uuid4())
    turf_payload = {"name": "Docker Arena", "location": "Container Zone", "price_per_hour": 100.0}
    res_turf = requests.post(f"{TURF_URL}/turfs", json=turf_payload, headers={"Idempotency-Key": idem_key_turf})
    print(f"Step 1: Turf Creation Status -> {res_turf.status_code}")
    turf_id = res_turf.json().get("id", 1)

    # 3. Step 2: Hold Booking Slot
    hold_payload = {
        "turf_id": turf_id,
        "booking_date": "2026-11-05",
        "start_time": "19:00:00",
        "end_time": "20:00:00",
        "user_id": "docker_user_1",
        "amount": 1000.0
    }
    res_hold = requests.post(f"{BOOKING_URL}/bookings/hold", json=hold_payload)
    print(f"Step 2: Slot Hold Status     -> {res_hold.status_code}")
    assert res_hold.status_code == 201
    booking_id = res_hold.json()["id"]

    # 4. Step 3: Payment Charge (Idempotent)
    idem_key_pay = str(uuid.uuid4())
    pay_payload = {"booking_id": booking_id, "amount": 100.0}
    res_pay = requests.post(f"{PAYMENT_URL}/payments/charge", json=pay_payload, headers={"Idempotency-Key": idem_key_pay})
    print(f"Step 3: Payment Charge Status  -> {res_pay.status_code}")
    assert res_pay.status_code == 200
    pay_ref = res_pay.json()["payment_reference"]

    # 5. Step 4: Confirm Booking
    confirm_payload = {"status": "CONFIRMED", "payment_reference": pay_ref}
    res_confirm = requests.post(f"{BOOKING_URL}/bookings/{booking_id}/confirm", json=confirm_payload)
    print(f"Step 4: Confirm Booking Status -> {res_confirm.status_code}")
    assert res_confirm.status_code == 200

    # 6. Step 5: Send Notification
    notif_payload = {"user_id": "docker_user_1", "booking_id": booking_id, "channel": "EMAIL", "message": "Booking Confirmed!"}
    res_notif = requests.post(f"{NOTIF_URL}/notifications/send", json=notif_payload)
    print(f"Step 5: Notification Status   -> {res_notif.status_code}")
    assert res_notif.status_code == 200

    print("\n[SUCCESS] E2E Containerized Application Workflow Passed Successfully!")

if __name__ == "__main__":
    run_e2e_deployment_test()