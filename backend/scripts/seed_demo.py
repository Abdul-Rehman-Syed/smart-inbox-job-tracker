from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select

from app.database import SessionLocal
from app.models import Job, JobStatus, JobStatusHistory, User
from app.security import hash_password

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "password123"


def seed_demo_data():
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if not user:
            user = User(
                email=DEMO_EMAIL,
                full_name="Demo User",
                hashed_password=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.full_name = "Demo User"
            user.hashed_password = hash_password(DEMO_PASSWORD)
            db.commit()
            db.refresh(user)

        db.execute(delete(JobStatusHistory).where(JobStatusHistory.user_id == user.id))
        db.execute(delete(Job).where(Job.user_id == user.id))

        now = datetime.now(timezone.utc)
        demo_jobs = [
            {
                "company": "Stripe",
                "job_title": "Frontend Engineer",
                "job_url": "https://stripe.com/jobs",
                "date_applied": now - timedelta(days=2),
                "status": JobStatus.INTERVIEW,
                "salary_min": 135000,
                "salary_max": 175000,
            },
            {
                "company": "Notion",
                "job_title": "Full Stack Engineer",
                "job_url": "https://www.notion.so/careers",
                "date_applied": now - timedelta(days=5),
                "status": JobStatus.APPLIED,
                "salary_min": 120000,
                "salary_max": 160000,
            },
            {
                "company": "Vercel",
                "job_title": "Software Engineer",
                "job_url": "https://vercel.com/careers",
                "date_applied": now - timedelta(days=9),
                "status": JobStatus.OFFER,
                "salary_min": 140000,
                "salary_max": 190000,
            },
            {
                "company": "Spotify",
                "job_title": "Backend Engineer",
                "job_url": "https://www.lifeatspotify.com/jobs",
                "date_applied": now - timedelta(days=14),
                "status": JobStatus.REJECTED,
                "salary_min": 115000,
                "salary_max": 150000,
            },
            {
                "company": "Linear",
                "job_title": "Product Engineer",
                "job_url": "https://linear.app/careers",
                "date_applied": now - timedelta(days=21),
                "status": JobStatus.INTERVIEW,
                "salary_min": 130000,
                "salary_max": 170000,
            },
            {
                "company": "Figma",
                "job_title": "Design Systems Engineer",
                "job_url": "https://www.figma.com/careers",
                "date_applied": now - timedelta(days=32),
                "status": JobStatus.APPLIED,
                "salary_min": 125000,
                "salary_max": 165000,
            },
            {
                "company": "OpenAI",
                "job_title": "Developer Experience Engineer",
                "job_url": "https://openai.com/careers",
                "date_applied": now - timedelta(days=41),
                "status": JobStatus.APPLIED,
                "salary_min": 150000,
                "salary_max": 210000,
            },
            {
                "company": "Airbnb",
                "job_title": "Platform Engineer",
                "job_url": "https://careers.airbnb.com",
                "date_applied": now - timedelta(days=52),
                "status": JobStatus.REJECTED,
                "salary_min": 128000,
                "salary_max": 168000,
            },
        ]

        for job_data in demo_jobs:
            job = Job(user_id=user.id, **job_data)
            db.add(job)
            db.flush()
            db.add(
                JobStatusHistory(
                    job_id=job.id,
                    user_id=user.id,
                    old_status=None,
                    new_status=job.status.value,
                    source="seed",
                    note="Demo application created",
                )
            )
        db.commit()
        print(f"Seeded {len(demo_jobs)} jobs for {DEMO_EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
