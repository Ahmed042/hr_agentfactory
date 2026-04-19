"""Tests for department endpoints"""


def test_create_department(client, auth_headers):
    response = client.post("/api/departments/", json={
        "name": "Engineering",
        "description": "Software engineering department",
    })
    assert response.status_code == 200


def test_get_departments(client):
    client.post("/api/departments/", json={"name": "HR"})
    response = client.get("/api/departments/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
