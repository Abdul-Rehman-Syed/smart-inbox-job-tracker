def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"


def test_not_found_response_shape(client):
    response = client.get("/api/jobs/11111111-1111-1111-1111-111111111111")
    assert response.status_code == 404
    assert response.json()["success"] is False


def test_invalid_uuid_returns_validation_error(client):
    response = client.get("/api/jobs/not-a-uuid")
    assert response.status_code == 422


def test_missing_required_fields(client):
    response = client.post("/api/jobs", json={"company": "Missing Fields"})
    assert response.status_code == 422


def test_salary_min_cannot_exceed_max(client, job_payload):
    job_payload["salary_min"] = 150000
    job_payload["salary_max"] = 100000
    response = client.post("/api/jobs", json=job_payload)
    assert response.status_code == 422
