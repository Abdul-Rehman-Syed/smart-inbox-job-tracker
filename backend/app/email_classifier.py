from dataclasses import dataclass
import re


STATUS_PRIORITY = ("Offer", "Rejected", "Interview", "Applied")

STATUS_KEYWORDS = {
    "Applied": (
        "application received",
        "thank you for applying",
        "thanks for applying",
        "application submitted",
        "we received your application",
        "your application has been received",
    ),
    "Interview": (
        "interview",
        "schedule a call",
        "schedule an interview",
        "next round",
        "availability",
        "meet with",
        "phone screen",
        "technical screen",
    ),
    "Rejected": (
        "unfortunately",
        "not moving forward",
        "decided not to proceed",
        "other candidates",
        "will not be proceeding",
        "not selected",
        "pursue other candidates",
    ),
    "Offer": (
        "offer",
        "pleased to offer",
        "congratulations",
        "compensation",
        "offer letter",
    ),
}

COMPANY_SUFFIXES = (
    "inc",
    "inc.",
    "gmbh",
    "ltd",
    "ltd.",
    "llc",
    "corp",
    "corp.",
    "corporation",
    "company",
)


@dataclass(frozen=True)
class EmailClassification:
    status: str
    matched_keywords: list[str]
    company: str | None = None
    job_title: str | None = None
    note: str | None = None


def classify_email(subject: str | None, snippet: str | None, sender: str | None = None) -> EmailClassification:
    text = _normalize_text(" ".join(part for part in (subject, snippet) if part))
    matches = {
        status: [keyword for keyword in keywords if keyword in text] for status, keywords in STATUS_KEYWORDS.items()
    }
    status = next((candidate for candidate in STATUS_PRIORITY if matches[candidate]), "Unknown")
    matched_keywords = matches.get(status, [])

    company = extract_company(subject, sender)
    job_title = extract_job_title(subject)
    note = "Matched keywords: " + ", ".join(matched_keywords) if matched_keywords else "No status keywords matched"

    return EmailClassification(
        status=status,
        matched_keywords=matched_keywords,
        company=company,
        job_title=job_title,
        note=note,
    )


def extract_company(subject: str | None, sender: str | None = None) -> str | None:
    subject_company = _extract_company_from_subject(subject)
    if subject_company:
        return subject_company
    return _extract_company_from_sender(sender)


def extract_job_title(subject: str | None) -> str | None:
    if not subject:
        return None

    patterns = (
        r"application submitted for (?P<title>.+?)(?: at | - |$)",
        r"application (?:for|to) (?P<title>.+?)(?: at | - |$)",
        r"your application for (?P<title>.+?)(?: at | - |$)",
        r"interview (?:for|with).*?(?P<title>[A-Z][A-Za-z0-9 /+-]+ Engineer|[A-Z][A-Za-z0-9 /+-]+ Developer)",
        r"(?P<title>[A-Z][A-Za-z0-9 /+-]+ Engineer|[A-Z][A-Za-z0-9 /+-]+ Developer)",
    )
    for pattern in patterns:
        match = re.search(pattern, subject, flags=re.IGNORECASE)
        if match:
            return _clean_title(match.group("title"))
    return None


def normalize_company(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9 ]+", " ", value).lower()
    words = [word for word in normalized.split() if word not in COMPANY_SUFFIXES]
    return " ".join(words)


def _extract_company_from_subject(subject: str | None) -> str | None:
    if not subject:
        return None

    patterns = (
        r" at (?P<company>[A-Z][A-Za-z0-9&. -]{1,80})",
        r" from (?P<company>[A-Z][A-Za-z0-9&. -]{1,80})",
        r" with (?P<company>[A-Z][A-Za-z0-9&. -]{1,80})",
        r"(?P<company>[A-Z][A-Za-z0-9&. -]{1,80}) careers",
    )
    for pattern in patterns:
        match = re.search(pattern, subject)
        if match:
            return _clean_company(match.group("company"))
    return None


def _extract_company_from_sender(sender: str | None) -> str | None:
    if not sender or "@" not in sender:
        return None
    domain = sender.split("@", 1)[1].split(">", 1)[0].lower()
    name = domain.split(".", 1)[0]
    if name in {"mail", "email", "notifications", "noreply", "no-reply", "jobs", "careers"}:
        return None
    return _clean_company(name.replace("-", " "))


def _clean_company(value: str) -> str:
    cleaned = re.split(r"[:|,;]", value, maxsplit=1)[0]
    cleaned = re.split(
        r"\s+(?:has|have|is|was|will|would|invites|invited|regarding)\b",
        cleaned,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -.")
    return cleaned.title() if cleaned else ""


def _clean_title(value: str) -> str:
    cleaned = re.split(r" at | - | \| ", value, maxsplit=1, flags=re.IGNORECASE)[0]
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -.")
    return cleaned.title() if cleaned else ""


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).lower()
