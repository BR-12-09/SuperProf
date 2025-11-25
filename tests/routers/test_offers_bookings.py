import jwt, os

def login(client, email, password):
    r = client.post("/auth/token", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]

def auth_hdr(token): return {"Authorization": f"Bearer {token}"}

def test_full_flow_and_negatives(client, db_session, tutor_user, student_user):
    # login
    token_tutor = login(client, tutor_user.email, "pass")
    token_student = login(client, student_user.email, "pass")

    # tutor creates an offer
    r = client.post("/offers/", headers=auth_hdr(token_tutor),
                    json={"subject":"Python","description":"Bases","price_hour":30})
    assert r.status_code == 201, r.text
    offer = r.json()
    offer_id = offer["id"]
    assert offer["tutor_id"] == str(tutor_user.id)

    # student creates a booking
    r = client.post("/bookings/", headers=auth_hdr(token_student),
                    json={"offer_id": offer_id})
    assert r.status_code == 201, r.text
    booking_id = r.json()["id"]

    # tutor accepts
    r = client.post(f"/bookings/{booking_id}/ACCEPT", headers=auth_hdr(token_tutor))
    assert r.status_code == 200
    assert r.json()["status"] == "ACCEPTED"

    # ---------- negatives ----------
    # no auth
    assert client.post("/offers/", json={"subject":"JS","description":"Init","price_hour":20}).status_code in (401,422)
    assert client.post("/bookings/", json={"offer_id": offer_id}).status_code in (401,422)

    # student tries to create an offer
    assert client.post("/offers/", headers=auth_hdr(token_student),
                       json={"subject":"JS","description":"Init","price_hour":20}).status_code == 403

    # invalid action
    assert client.post(f"/bookings/{booking_id}/MAYBE", headers=auth_hdr(token_tutor)).status_code == 400

    # 404 booking not found
    assert client.post("/bookings/00000000-0000-0000-0000-000000000000/ACCEPT",
                       headers=auth_hdr(token_tutor)).status_code == 404
