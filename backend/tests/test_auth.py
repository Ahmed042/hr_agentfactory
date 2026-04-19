"""Tests for authentication endpoints"""


def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "email": "newuser@test.com",
        "password": "password123",
        "name": "New User",
        "role": "recruiter",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["user"]["email"] == "newuser@test.com"
    assert data["user"]["role"] == "recruiter"


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "email": "dup@test.com",
        "password": "password123",
        "name": "User1",
        "role": "recruiter",
    })
    response = client.post("/api/auth/register", json={
        "email": "dup@test.com",
        "password": "password456",
        "name": "User2",
        "role": "recruiter",
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_invalid_role(client):
    response = client.post("/api/auth/register", json={
        "email": "invalid@test.com",
        "password": "password123",
        "role": "superadmin",
    })
    assert response.status_code == 400
    assert "Invalid role" in response.json()["detail"]


def test_register_short_password(client):
    response = client.post("/api/auth/register", json={
        "email": "short@test.com",
        "password": "123",
        "role": "recruiter",
    })
    assert response.status_code == 400
    assert "8 characters" in response.json()["detail"]


def test_login_success(client):
    client.post("/api/auth/register", json={
        "email": "login@test.com",
        "password": "password123",
        "name": "Login User",
        "role": "admin",
    })
    response = client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "email": "wrong@test.com",
        "password": "password123",
        "role": "recruiter",
    })
    response = client.post("/api/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_me_endpoint(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "testadmin@test.com"


def test_me_no_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 403
