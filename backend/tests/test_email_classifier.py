from app.email_classifier import classify_email, extract_company, extract_job_title, normalize_company


def test_classifies_application_confirmation():
    result = classify_email(
        subject="Your application for Frontend Engineer at Acme has been received",
        snippet="Thank you for applying. We received your application.",
        sender="jobs@acme.com",
    )

    assert result.status == "Applied"
    assert result.company == "Acme"
    assert result.job_title == "Frontend Engineer"
    assert "we received your application" in result.matched_keywords


def test_classifies_interview_invitation():
    result = classify_email(
        subject="Interview for Backend Engineer at Globex",
        snippet="Please share your availability to schedule a call with the hiring team.",
    )

    assert result.status == "Interview"
    assert result.company == "Globex"
    assert result.job_title == "Backend Engineer"


def test_classifies_rejection():
    result = classify_email(
        subject="Update from Initech",
        snippet="Unfortunately, we decided not to proceed and will pursue other candidates.",
    )

    assert result.status == "Rejected"
    assert "unfortunately" in result.matched_keywords


def test_classifies_offer_over_interview_keywords():
    result = classify_email(
        subject="Offer letter from Hooli",
        snippet="Congratulations. We are pleased to offer compensation after your final interview.",
    )

    assert result.status == "Offer"


def test_unknown_when_no_keywords_match():
    result = classify_email(subject="Weekly newsletter", snippet="Here are product updates.")

    assert result.status == "Unknown"
    assert result.matched_keywords == []
    assert result.note == "No status keywords matched"


def test_extracts_company_from_sender_domain():
    assert extract_company(None, "recruiting@stripe.com") == "Stripe"


def test_ignores_generic_sender_domain():
    assert extract_company(None, "noreply@notifications.example.com") is None


def test_extracts_job_title_from_subject():
    assert (
        extract_job_title("Application submitted for Senior Python Developer at Example") == "Senior Python Developer"
    )


def test_normalizes_company_suffixes():
    assert normalize_company("Acme GmbH") == "acme"
    assert normalize_company("Globex Corporation") == "globex"
