from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.email_processor import process_email_event
from app.gmail_client import fetch_recent_job_emails
from app.gmail_oauth import build_gmail_authorization_url, decode_gmail_oauth_state, exchange_gmail_code
from app.models import EmailConnection, EmailEvent, User
from app.schemas import ApiResponse, EmailConnectionStatus, EmailEventRead, EmailSyncSummary, GmailConnectUrl
from app.security import get_current_user

router = APIRouter(prefix="/api/email", tags=["email"])


def _get_gmail_connection(db: Session, user_id: UUID) -> EmailConnection | None:
    return db.scalar(
        select(EmailConnection).where(EmailConnection.user_id == user_id, EmailConnection.provider == "gmail")
    )


@router.get("/gmail/status", response_model=ApiResponse[EmailConnectionStatus])
def get_gmail_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connection = _get_gmail_connection(db, current_user.id)
    return ApiResponse(
        data=EmailConnectionStatus(
            connected=connection is not None,
            connection=connection,
        )
    )


@router.get("/gmail/connect", response_model=ApiResponse[GmailConnectUrl])
def connect_gmail(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=GmailConnectUrl(authorization_url=build_gmail_authorization_url(current_user.id)))


@router.get("/gmail/callback", include_in_schema=False)
def gmail_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    frontend_url = get_settings().frontend_url
    if error:
        return RedirectResponse(f"{frontend_url}?gmail=error")
    if not code or not state:
        return RedirectResponse(f"{frontend_url}?gmail=missing_code")

    user_id = decode_gmail_oauth_state(state)
    token_data = exchange_gmail_code(code)
    connection = _get_gmail_connection(db, user_id)
    if connection:
        for key, value in token_data.items():
            setattr(connection, key, value)
    else:
        db.add(EmailConnection(user_id=user_id, provider="gmail", **token_data))
    db.commit()
    return RedirectResponse(f"{frontend_url}?gmail=connected")


@router.post("/gmail/disconnect", response_model=ApiResponse[dict])
def disconnect_gmail(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connection = _get_gmail_connection(db, current_user.id)
    if not connection:
        return ApiResponse(data={"connected": False}, message="Gmail is not connected")
    db.delete(connection)
    db.commit()
    return ApiResponse(data={"connected": False}, message="Gmail disconnected")


@router.post("/sync", response_model=ApiResponse[EmailSyncSummary])
def sync_gmail(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connection = _get_gmail_connection(db, current_user.id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connect Gmail before syncing email events",
        )
    messages = fetch_recent_job_emails(connection.encrypted_refresh_token)
    summary = EmailSyncSummary(scanned=len(messages))
    for message in messages:
        event = process_email_event(db, current_user.id, message)
        if event.processing_status == "Created":
            summary.created_jobs += 1
        elif event.processing_status == "Updated":
            summary.updated_jobs += 1
        elif event.processing_status == "NeedsReview":
            summary.needs_review += 1
        else:
            summary.skipped += 1

    connection.last_sync_at = datetime.now(timezone.utc)
    db.commit()
    return ApiResponse(data=summary, message="Gmail sync completed")


@router.get("/events", response_model=ApiResponse[list[EmailEventRead]])
def list_email_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = db.scalars(
        select(EmailEvent)
        .where(EmailEvent.user_id == current_user.id, EmailEvent.provider == "gmail")
        .order_by(EmailEvent.received_at.desc(), EmailEvent.created_at.desc())
    ).all()
    return ApiResponse(data=events)
