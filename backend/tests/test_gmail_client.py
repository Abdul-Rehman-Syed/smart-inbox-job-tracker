import base64
from datetime import timezone

from app.gmail_client import parse_gmail_message


def test_parse_gmail_message_extracts_metadata_and_url():
    body = base64.urlsafe_b64encode(b"Apply here: https://example.com/jobs/frontend").decode("utf-8").rstrip("=")

    message = parse_gmail_message(
        {
            "id": "msg-1",
            "threadId": "thread-1",
            "snippet": "Thank you for applying",
            "internalDate": "1778752800000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Acme Careers <jobs@acme.com>"},
                    {"name": "Subject", "value": "Your application for Frontend Engineer at Acme"},
                    {"name": "Date", "value": "Thu, 14 May 2026 10:00:00 +0000"},
                ],
                "parts": [{"mimeType": "text/plain", "body": {"data": body}}],
            },
        }
    )

    assert message.message_id == "msg-1"
    assert message.thread_id == "thread-1"
    assert message.sender == "Acme Careers <jobs@acme.com>"
    assert message.subject == "Your application for Frontend Engineer at Acme"
    assert message.received_at.tzinfo == timezone.utc
    assert message.job_url == "https://example.com/jobs/frontend"


def test_parse_gmail_message_falls_back_to_internal_date():
    message = parse_gmail_message(
        {
            "id": "msg-2",
            "internalDate": "1778752800000",
            "payload": {"headers": [{"name": "Date", "value": "not a real date"}]},
        }
    )

    assert message.received_at.year == 2026


def test_parse_gmail_message_handles_missing_body():
    message = parse_gmail_message({"id": "msg-3", "payload": {"headers": []}})

    assert message.message_id == "msg-3"
    assert message.job_url is None
