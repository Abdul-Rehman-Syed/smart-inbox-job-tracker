from datetime import datetime, timezone

from app.models import EmailConnection, EmailEvent


def test_gmail_status_disconnected(client):
    response = client.get("/api/email/gmail/status")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["provider"] == "gmail"
    assert data["connected"] is False
    assert data["connection"] is None


def test_gmail_sync_requires_connection(client):
    response = client.post("/api/email/sync")
    assert response.status_code == 400
    assert response.json()["message"] == "Connect Gmail before syncing email events"


def test_gmail_events_empty(client):
    response = client.get("/api/email/events")
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_gmail_status_connected(client, db_session):
    user_id = _current_user_id(client)
    db_session.add(
        EmailConnection(
            user_id=user_id,
            provider="gmail",
            provider_email="test@gmail.com",
            encrypted_refresh_token="encrypted-token",
            scopes="https://www.googleapis.com/auth/gmail.readonly",
        )
    )
    db_session.commit()

    response = client.get("/api/email/gmail/status")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["connected"] is True
    assert data["connection"]["provider_email"] == "test@gmail.com"


def test_list_gmail_events(client, db_session):
    user_id = _current_user_id(client)
    db_session.add(
        EmailEvent(
            user_id=user_id,
            provider="gmail",
            message_id="msg-1",
            thread_id="thread-1",
            sender="jobs@example.com",
            subject="Interview invitation",
            received_at=datetime.now(timezone.utc),
            detected_company="Acme",
            detected_job_title="Frontend Engineer",
            detected_status="Interview",
            processing_status="Updated",
            note="Matched interview keyword",
        )
    )
    db_session.commit()

    response = client.get("/api/email/events")

    assert response.status_code == 200
    event = response.json()["data"][0]
    assert event["message_id"] == "msg-1"
    assert event["detected_status"] == "Interview"
    assert event["processing_status"] == "Updated"


def test_disconnect_gmail(client, db_session):
    user_id = _current_user_id(client)
    db_session.add(
        EmailConnection(
            user_id=user_id,
            provider="gmail",
            provider_email="test@gmail.com",
            encrypted_refresh_token="encrypted-token",
            scopes="https://www.googleapis.com/auth/gmail.readonly",
        )
    )
    db_session.commit()

    response = client.post("/api/email/gmail/disconnect")

    assert response.status_code == 200
    assert response.json()["data"]["connected"] is False
    assert client.get("/api/email/gmail/status").json()["data"]["connected"] is False


def _current_user_id(client):
    return client.get("/api/auth/me").json()["data"]["id"]
