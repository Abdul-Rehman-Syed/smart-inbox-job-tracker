from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EmailConnection, EmailEvent, User
from app.schemas import ApiResponse, EmailConnectionStatus, EmailEventRead, EmailSyncSummary
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
    return ApiResponse(data=EmailSyncSummary(), message="Gmail sync is not implemented yet")


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
