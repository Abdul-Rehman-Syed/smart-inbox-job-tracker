from datetime import datetime, timezone

from app.email_processor import IncomingEmail, process_email_event
from app.models import EmailEvent, Job, JobStatus, User
from app.security import hash_password


def test_process_email_creates_job_when_application_has_url(db_session):
    user_id = _user_id(db_session)

    event = process_email_event(
        db_session,
        user_id,
        IncomingEmail(
            message_id="msg-create",
            sender="jobs@acme.com",
            subject="Your application for Frontend Engineer at Acme has been received",
            snippet="Thank you for applying. We received your application.",
            received_at=datetime.now(timezone.utc),
            job_url="https://example.com/acme/frontend",
        ),
    )
    db_session.commit()

    job = db_session.query(Job).one()
    assert job.company == "Acme"
    assert job.job_title == "Frontend Engineer"
    assert job.status == JobStatus.APPLIED
    assert event.processing_status == "Created"
    assert event.job_id == job.id


def test_process_email_updates_existing_job_status(db_session):
    user_id = _user_id(db_session)
    job = _create_job(db_session, user_id)

    event = process_email_event(
        db_session,
        user_id,
        IncomingEmail(
            message_id="msg-interview",
            sender="recruiting@acme.com",
            subject="Interview for Frontend Engineer at Acme",
            snippet="Please share your availability to schedule a call.",
        ),
    )
    db_session.commit()
    db_session.refresh(job)

    assert job.status == JobStatus.INTERVIEW
    assert event.processing_status == "Updated"
    assert job.status_history[0].source == "email"
    assert job.status_history[0].old_status == "Applied"
    assert job.status_history[0].new_status == "Interview"


def test_process_email_marks_uncertain_status_as_needs_review(db_session):
    user_id = _user_id(db_session)

    event = process_email_event(
        db_session,
        user_id,
        IncomingEmail(
            message_id="msg-rejection",
            sender="noreply@example.com",
            subject="Application update",
            snippet="Unfortunately, we decided not to proceed.",
        ),
    )
    db_session.commit()

    assert db_session.query(Job).count() == 0
    assert event.processing_status == "NeedsReview"
    assert event.detected_status == "Rejected"


def test_process_email_skips_unknown_messages(db_session):
    user_id = _user_id(db_session)

    event = process_email_event(
        db_session,
        user_id,
        IncomingEmail(
            message_id="msg-newsletter",
            subject="Weekly product newsletter",
            snippet="Here are this week's product updates.",
        ),
    )
    db_session.commit()

    assert event.processing_status == "Skipped"
    assert event.detected_status == "Unknown"


def test_process_email_skips_duplicate_messages(db_session):
    user_id = _user_id(db_session)
    db_session.add(
        EmailEvent(
            user_id=user_id,
            provider="gmail",
            message_id="msg-duplicate",
            processing_status="Created",
        )
    )
    db_session.commit()

    event = process_email_event(db_session, user_id, IncomingEmail(message_id="msg-duplicate"))
    db_session.commit()

    assert event.processing_status == "Skipped"
    assert db_session.query(EmailEvent).count() == 1


def _create_job(db_session, user_id):
    job = Job(
        user_id=user_id,
        company="Acme",
        job_title="Frontend Engineer",
        job_url="https://example.com/acme/frontend",
        date_applied=datetime.now(timezone.utc),
        status=JobStatus.APPLIED,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


def _user_id(db_session):
    user = User(
        email="email-processor@example.com",
        full_name="Email Processor",
        hashed_password=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user.id
