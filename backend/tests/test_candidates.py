"""Tests for candidate endpoints"""


def test_create_candidate(client):
    response = client.post("/api/candidates/", json={
        "email": "candidate@test.com",
        "job_role": "Software Engineer",
        "name": "Test Candidate",
        "source": "linkedin",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["candidate_id"]


def test_create_duplicate_candidate(client):
    client.post("/api/candidates/", json={
        "email": "dup@test.com",
        "job_role": "Developer",
    })
    response = client.post("/api/candidates/", json={
        "email": "dup@test.com",
        "job_role": "Designer",
    })
    assert response.status_code == 400


def test_get_candidates(client):
    client.post("/api/candidates/", json={
        "email": "list@test.com",
        "job_role": "QA Engineer",
    })
    response = client.get("/api/candidates/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_candidate_by_id(client):
    create = client.post("/api/candidates/", json={
        "email": "byid@test.com",
        "job_role": "DevOps",
    })
    cid = create.json()["candidate_id"]
    response = client.get(f"/api/candidates/{cid}")
    assert response.status_code == 200
    assert response.json()["email"] == "byid@test.com"


def test_get_candidate_not_found(client):
    response = client.get("/api/candidates/99999")
    assert response.status_code == 404


def test_update_candidate(client):
    create = client.post("/api/candidates/", json={
        "email": "update@test.com",
        "job_role": "Frontend",
    })
    cid = create.json()["candidate_id"]
    response = client.put(f"/api/candidates/{cid}", json={
        "status": "screening",
        "stage": "screening",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "screening"


def test_delete_candidate(client):
    create = client.post("/api/candidates/", json={
        "email": "delete@test.com",
        "job_role": "Backend",
    })
    cid = create.json()["candidate_id"]
    response = client.delete(f"/api/candidates/{cid}")
    assert response.status_code == 200
    assert response.json()["message"] == "Candidate deleted"

    # Verify deleted
    response = client.get(f"/api/candidates/{cid}")
    assert response.status_code == 404


def test_filter_candidates_by_status(client):
    client.post("/api/candidates/", json={
        "email": "filter1@test.com",
        "job_role": "Engineer",
    })
    response = client.get("/api/candidates/?status=applied")
    assert response.status_code == 200
    for c in response.json():
        assert c["status"] == "applied"


def test_search_candidates(client):
    client.post("/api/candidates/", json={
        "email": "search@test.com",
        "job_role": "Data Scientist",
        "name": "Searchable Name",
    })
    response = client.get("/api/candidates/?search=Searchable")
    assert response.status_code == 200
    assert len(response.json()) >= 1
