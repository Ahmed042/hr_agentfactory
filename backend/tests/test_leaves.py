"""Tests for leave management endpoints"""


def test_create_leave_no_employee(client):
    response = client.post("/api/leaves/", json={
        "employee_id": 99999,
        "leave_type": "sick",
        "start_date": "2026-04-20",
        "end_date": "2026-04-22",
    })
    assert response.status_code == 404


def test_create_leave_invalid_type(client):
    # First create an employee
    emp_resp = client.post("/api/employees/", json={
        "email": "leave_emp@test.com",
        "name": "Leave Employee",
        "role": "Engineer",
    })
    emp_id = emp_resp.json()["id"]

    response = client.post("/api/leaves/", json={
        "employee_id": emp_id,
        "leave_type": "invalid",
        "start_date": "2026-04-20",
        "end_date": "2026-04-22",
    })
    assert response.status_code == 400


def test_create_and_list_leaves(client):
    emp_resp = client.post("/api/employees/", json={
        "email": "leave2@test.com",
        "name": "Leave Test",
        "role": "Manager",
    })
    emp_id = emp_resp.json()["id"]

    client.post("/api/leaves/", json={
        "employee_id": emp_id,
        "leave_type": "annual",
        "start_date": "2026-05-01",
        "end_date": "2026-05-05",
        "reason": "Vacation",
    })

    response = client.get("/api/leaves/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_approve_leave(client, auth_headers):
    emp_resp = client.post("/api/employees/", json={
        "email": "approve@test.com",
        "name": "Approve Test",
        "role": "Developer",
    })
    emp_id = emp_resp.json()["id"]

    create_resp = client.post("/api/leaves/", json={
        "employee_id": emp_id,
        "leave_type": "sick",
        "start_date": "2026-04-25",
        "end_date": "2026-04-25",
    })
    leave_id = create_resp.json()["id"]

    response = client.put(f"/api/leaves/{leave_id}", json={"status": "approved"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
