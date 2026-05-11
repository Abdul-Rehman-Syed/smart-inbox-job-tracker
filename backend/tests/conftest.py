import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_job_tracker.db"
os.environ["ENVIRONMENT"] = "test"

from app.database import Base, get_db  # noqa: E402
from main import app  # noqa: E402

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_job_tracker.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def job_payload():
    return {
        "company": "Acme Corp",
        "job_title": "Frontend Engineer",
        "job_url": "https://example.com/jobs/frontend",
        "date_applied": datetime.now(timezone.utc).isoformat(),
        "status": "Applied",
        "salary_min": 90000,
        "salary_max": 120000,
    }
