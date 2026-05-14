import base64
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.config import get_settings
from app.email_processor import IncomingEmail
from app.gmail_oauth import GOOGLE_TOKEN_URL, decrypt_token

GMAIL_MESSAGES_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
JOB_EMAIL_QUERY = (
    'newer_than:7d (applied OR application OR interview OR rejected OR rejection OR offer OR "not moving forward")'
)


def fetch_recent_job_emails(encrypted_refresh_token: str, max_results: int = 50) -> list[IncomingEmail]:
    access_token = refresh_gmail_access_token(decrypt_token(encrypted_refresh_token))
    headers = {"Authorization": f"Bearer {access_token}"}

    list_response = httpx.get(
        GMAIL_MESSAGES_URL,
        headers=headers,
        params={"q": JOB_EMAIL_QUERY, "maxResults": max_results},
        timeout=15,
    )
    if list_response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not list Gmail messages")

    messages = list_response.json().get("messages", [])
    parsed_messages = []
    for item in messages[:max_results]:
        message_id = item.get("id")
        if not message_id:
            continue
        parsed_messages.append(fetch_gmail_message(message_id, access_token))
    return parsed_messages


def fetch_gmail_message(message_id: str, access_token: str) -> IncomingEmail:
    response = httpx.get(
        f"{GMAIL_MESSAGES_URL}/{message_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"format": "full"},
        timeout=15,
    )
    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not read a Gmail message")
    return parse_gmail_message(response.json())


def refresh_gmail_access_token(refresh_token: str) -> str:
    settings = get_settings()
    response = httpx.post(
        GOOGLE_TOKEN_URL,
        data={
            "client_id": settings.gmail_client_id,
            "client_secret": settings.gmail_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=15,
    )
    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not refresh Gmail access")

    access_token = response.json().get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google did not return an access token")
    return access_token


def parse_gmail_message(message: dict[str, Any]) -> IncomingEmail:
    payload = message.get("payload", {})
    headers = _headers_to_dict(payload.get("headers", []))
    received_at = _parse_received_at(headers.get("date"), message.get("internalDate"))
    body_text = _extract_body_text(payload)

    return IncomingEmail(
        message_id=message.get("id", ""),
        thread_id=message.get("threadId"),
        sender=headers.get("from"),
        subject=headers.get("subject"),
        snippet=message.get("snippet"),
        received_at=received_at,
        job_url=_extract_first_url(body_text),
    )


def _headers_to_dict(headers: list[dict[str, str]]) -> dict[str, str]:
    return {item.get("name", "").lower(): item.get("value", "") for item in headers}


def _parse_received_at(date_header: str | None, internal_date: str | None) -> datetime | None:
    if date_header:
        try:
            parsed = parsedate_to_datetime(date_header)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    if internal_date:
        try:
            return datetime.fromtimestamp(int(internal_date) / 1000, tz=timezone.utc)
        except (TypeError, ValueError):
            return None
    return None


def _extract_body_text(payload: dict[str, Any]) -> str:
    chunks = []
    body_data = payload.get("body", {}).get("data")
    if body_data:
        chunks.append(_decode_body_data(body_data))
    for part in payload.get("parts", []) or []:
        chunks.append(_extract_body_text(part))
    return "\n".join(chunk for chunk in chunks if chunk)


def _decode_body_data(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(f"{value}{padding}").decode("utf-8", errors="ignore")
    except (ValueError, TypeError):
        return ""


def _extract_first_url(value: str) -> str | None:
    match = re.search(r"https?://[^\s<>()\"']+", value)
    if not match:
        return None
    return match.group(0).rstrip(".,;]")
