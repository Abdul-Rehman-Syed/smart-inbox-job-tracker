import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import httpx
from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.config import get_settings
from app.security import ALGORITHM

GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_PROFILE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
STATE_EXPIRE_MINUTES = 10


def build_gmail_authorization_url(user_id: UUID) -> str:
    settings = get_settings()
    if not settings.gmail_oauth_configured:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gmail OAuth is not configured",
        )

    query = urlencode(
        {
            "client_id": settings.gmail_client_id,
            "redirect_uri": settings.gmail_redirect_uri,
            "response_type": "code",
            "scope": GMAIL_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": create_gmail_oauth_state(user_id),
        }
    )
    return f"{GOOGLE_AUTH_URL}?{query}"


def create_gmail_oauth_state(user_id: UUID) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=STATE_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "purpose": "gmail_oauth", "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_gmail_oauth_state(state: str) -> UUID:
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired Gmail connection state",
    )
    try:
        payload = jwt.decode(state, get_settings().secret_key, algorithms=[ALGORITHM])
        if payload.get("purpose") != "gmail_oauth" or not payload.get("sub"):
            raise credentials_exception
        return UUID(payload["sub"])
    except (JWTError, ValueError) as exc:
        raise credentials_exception from exc


def exchange_gmail_code(code: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.gmail_oauth_configured:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gmail OAuth is not configured",
        )

    token_response = httpx.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.gmail_client_id,
            "client_secret": settings.gmail_client_secret,
            "redirect_uri": settings.gmail_redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    if token_response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google rejected the Gmail authorization code",
        )

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    if not access_token or not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not return the required Gmail tokens",
        )

    profile_response = httpx.get(
        GMAIL_PROFILE_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    if profile_response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read the connected Gmail profile",
        )

    expires_in = int(token_data.get("expires_in", 3600))
    return {
        "provider_email": profile_response.json().get("emailAddress", "unknown@gmail.com"),
        "encrypted_refresh_token": encrypt_token(refresh_token),
        "scopes": token_data.get("scope", GMAIL_SCOPE),
        "access_token_expires_at": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
    }


def encrypt_token(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_token(value: str) -> str:
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")


def _fernet() -> Fernet:
    settings = get_settings()
    source = settings.email_token_encryption_key or settings.secret_key
    digest = hashlib.sha256(source.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))
