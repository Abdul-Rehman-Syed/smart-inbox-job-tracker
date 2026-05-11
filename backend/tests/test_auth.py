def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "password123", "full_name": "New User"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["user"]["email"] == "new@example.com"


def test_register_duplicate_email(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 400


def test_login_user(client):
    response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "test@example.com"


def test_login_rejects_bad_password(client):
    response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong-password"})
    assert response.status_code == 401


def test_get_me(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "test@example.com"


def test_jobs_require_auth(client, job_payload):
    client.headers.pop("Authorization")
    response = client.get("/api/jobs")
    assert response.status_code == 403
