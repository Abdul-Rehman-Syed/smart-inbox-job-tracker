from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.email_classifier import classify_email, normalize_company
from app.models import EmailEvent, Job, JobStatus, JobStatusHistory


@dataclass(frozen=True)
class IncomingEmail:
    message_id: str
    thread_id: str | None = None
    sender: str | None = None
    subject: str | None = None
    snippet: str | None = None
    received_at: datetime | None = None
    job_url: str | None = None


def process_email_event(db: Session, user_id: UUID, email: IncomingEmail) -> EmailEvent:
    existing_event = db.scalar(
        select(EmailEvent).where(
            EmailEvent.user_id == user_id,
            EmailEvent.provider == "gmail",
            EmailEvent.message_id == email.message_id,
        )
    )
    if existing_event:
        existing_event.processing_status = "Skipped"
        existing_event.note = "Message was already processed"
        return existing_event

    classification = classify_email(email.subject, email.snippet, email.sender)
    job = _find_matching_job(db, user_id, classification.company, classification.job_title)
    processing_status = "NeedsReview"

    if classification.status == "Unknown":
        processing_status = "Skipped"
    elif job:
        processing_status = _update_job_status_from_email(db, user_id, job, classification.status, classification.note)
    elif _can_create_job(classification.company, classification.job_title, email.job_url, classification.status):
        job = _create_job_from_email(db, user_id, email, classification.company, classification.job_title)
        processing_status = "Created"

    event = EmailEvent(
        user_id=user_id,
        job_id=job.id if job else None,
        provider="gmail",
        message_id=email.message_id,
        thread_id=email.thread_id,
        sender=email.sender,
        subject=email.subject,
        received_at=email.received_at,
        detected_company=classification.company,
        detected_job_title=classification.job_title,
        detected_status=classification.status,
        processing_status=processing_status,
        note=classification.note,
    )
    db.add(event)
    return event


def _find_matching_job(db: Session, user_id: UUID, company: str | None, job_title: str | None) -> Job | None:
    if not company:
        return None

    jobs = db.scalars(select(Job).where(Job.user_id == user_id)).all()
    normalized_company = normalize_company(company)
    normalized_title = _normalize_title(job_title)

    for job in jobs:
        if normalize_company(job.company) != normalized_company:
            continue
        if normalized_title and _normalize_title(job.job_title) == normalized_title:
            return job
        if not normalized_title:
            return job
    return None


def _update_job_status_from_email(
    db: Session,
    user_id: UUID,
    job: Job,
    detected_status: str,
    note: str | None,
) -> str:
    try:
        next_status = JobStatus(detected_status)
    except ValueError:
        return "NeedsReview"

    if job.status == next_status:
        return "Skipped"

    old_status = job.status
    job.status = next_status
    db.add(
        JobStatusHistory(
            job_id=job.id,
            user_id=user_id,
            old_status=old_status.value,
            new_status=next_status.value,
            source="email",
            note=note,
        )
    )
    return "Updated"


def _can_create_job(company: str | None, job_title: str | None, job_url: str | None, status: str) -> bool:
    return bool(company and job_title and job_url and status == JobStatus.APPLIED.value)


def _create_job_from_email(
    db: Session,
    user_id: UUID,
    email: IncomingEmail,
    company: str | None,
    job_title: str | None,
) -> Job:
    job = Job(
        user_id=user_id,
        company=company or "Unknown",
        job_title=job_title or "Unknown role",
        job_url=email.job_url or "",
        date_applied=email.received_at or datetime.now(timezone.utc),
        status=JobStatus.APPLIED,
    )
    db.add(job)
    db.flush()
    db.add(
        JobStatusHistory(
            job_id=job.id,
            user_id=user_id,
            old_status=None,
            new_status=JobStatus.APPLIED.value,
            source="email",
            note="Application created from Gmail message",
        )
    )
    return job


def _normalize_title(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.lower().split())
