from datetime import datetime, timedelta, timezone


def create_job(client, payload):
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_create_job(client, job_payload):
    job = create_job(client, job_payload)
    assert job["company"] == "Acme Corp"
    assert job["status"] == "Applied"
    assert "id" in job


def test_list_jobs(client, job_payload):
    create_job(client, job_payload)
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


def test_get_single_job(client, job_payload):
    job = create_job(client, job_payload)
    response = client.get(f"/api/jobs/{job['id']}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == job["id"]


def test_update_job_status(client, job_payload):
    job = create_job(client, job_payload)
    response = client.put(f"/api/jobs/{job['id']}", json={"status": "Interview"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "Interview"
    assert data["status_history"][0]["old_status"] == "Applied"
    assert data["status_history"][0]["new_status"] == "Interview"


def test_create_job_records_initial_status_history(client, job_payload):
    job = create_job(client, job_payload)
    assert job["status_history"][0]["old_status"] is None
    assert job["status_history"][0]["new_status"] == "Applied"
    assert job["status_history"][0]["source"] == "manual"


def test_non_status_update_does_not_add_status_history(client, job_payload):
    job = create_job(client, job_payload)
    response = client.put(f"/api/jobs/{job['id']}", json={"company": "Globex"})
    assert response.status_code == 200
    assert len(response.json()["data"]["status_history"]) == 1


def test_update_job_company(client, job_payload):
    job = create_job(client, job_payload)
    response = client.put(f"/api/jobs/{job['id']}", json={"company": "Globex"})
    assert response.status_code == 200
    assert response.json()["data"]["company"] == "Globex"


def test_invalid_status_rejected(client, job_payload):
    job = create_job(client, job_payload)
    response = client.put(f"/api/jobs/{job['id']}", json={"status": "Ghosted"})
    assert response.status_code == 422


def test_delete_job(client, job_payload):
    job = create_job(client, job_payload)
    delete_response = client.delete(f"/api/jobs/{job['id']}")
    assert delete_response.status_code == 200
    get_response = client.get(f"/api/jobs/{job['id']}")
    assert get_response.status_code == 404


def test_delete_missing_job(client):
    response = client.delete("/api/jobs/11111111-1111-1111-1111-111111111111")
    assert response.status_code == 404


def test_filter_last_7_days(client, job_payload):
    recent = dict(job_payload)
    old = dict(job_payload)
    old["company"] = "Old Co"
    old["date_applied"] = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    create_job(client, recent)
    create_job(client, old)
    response = client.get("/api/jobs?date_range=7d")
    assert response.status_code == 200
    companies = [job["company"] for job in response.json()["data"]]
    assert companies == ["Acme Corp"]


def test_filter_last_30_days(client, job_payload):
    older = dict(job_payload)
    older["company"] = "Ancient Co"
    older["date_applied"] = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
    create_job(client, job_payload)
    create_job(client, older)
    response = client.get("/api/jobs?date_range=30d")
    assert len(response.json()["data"]) == 1


def test_filter_by_status(client, job_payload):
    rejected = dict(job_payload)
    rejected["company"] = "Nope Inc"
    rejected["status"] = "Rejected"
    create_job(client, job_payload)
    create_job(client, rejected)
    response = client.get("/api/jobs?status=Rejected")
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["status"] == "Rejected"


def test_stats_empty(client):
    response = client.get("/api/stats")
    stats = response.json()["data"]
    assert stats["total_applications"] == 0
    assert stats["pending"] == 0


def test_stats_counts(client, job_payload):
    interview = dict(job_payload)
    interview["company"] = "Acme Corp"
    interview["status"] = "Interview"
    rejected = dict(job_payload)
    rejected["company"] = "Globex"
    rejected["status"] = "Rejected"
    create_job(client, job_payload)
    create_job(client, interview)
    create_job(client, rejected)
    response = client.get("/api/stats")
    stats = response.json()["data"]
    assert stats["total_applications"] == 3
    assert stats["interviews"] == 1
    assert stats["rejections"] == 1
    assert stats["pending"] == 1
    assert stats["by_company"]["Acme Corp"] == 2


def test_stats_date_filter(client, job_payload):
    old = dict(job_payload)
    old["company"] = "Old Co"
    old["date_applied"] = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    create_job(client, job_payload)
    create_job(client, old)
    response = client.get("/api/stats?date_range=30d")
    assert response.json()["data"]["total_applications"] == 1


def test_update_salary_range_validation(client, job_payload):
    job = create_job(client, job_payload)
    response = client.put(f"/api/jobs/{job['id']}", json={"salary_min": 130000})
    assert response.status_code == 400


def test_create_offer_job(client, job_payload):
    job_payload["status"] = "Offer"
    response = client.post("/api/jobs", json=job_payload)
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "Offer"
