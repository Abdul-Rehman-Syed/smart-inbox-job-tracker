from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, JobStatus
from app.schemas import ApiResponse, JobCreate, JobRead, JobUpdate, Stats

router = APIRouter(prefix="/api", tags=["jobs"])

DateRange = Literal["all", "7d", "30d"]


def _date_cutoff(date_range: DateRange | None) -> datetime | None:
    now = datetime.now(timezone.utc)
    if date_range == "7d":
        return now - timedelta(days=7)
    if date_range == "30d":
        return now - timedelta(days=30)
    return None


def _get_job_or_404(db: Session, job_id: UUID) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found")
    return job


@router.post("/jobs", response_model=ApiResponse[JobRead], status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    values = payload.model_dump()
    values["job_url"] = str(payload.job_url)
    job = Job(**values)
    db.add(job)
    db.commit()
    db.refresh(job)
    return ApiResponse(data=job, message="Job application created")


@router.get("/jobs", response_model=ApiResponse[list[JobRead]])
def list_jobs(
    date_range: DateRange = Query(default="all"),
    status_filter: JobStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    stmt = select(Job).order_by(Job.date_applied.desc(), Job.created_at.desc())
    cutoff = _date_cutoff(date_range)
    if cutoff:
        stmt = stmt.where(Job.date_applied >= cutoff)
    if status_filter:
        stmt = stmt.where(Job.status == status_filter)
    jobs = db.scalars(stmt).all()
    return ApiResponse(data=jobs)


@router.get("/jobs/{job_id}", response_model=ApiResponse[JobRead])
def get_job(job_id: UUID, db: Session = Depends(get_db)):
    return ApiResponse(data=_get_job_or_404(db, job_id))


@router.put("/jobs/{job_id}", response_model=ApiResponse[JobRead])
def update_job(job_id: UUID, payload: JobUpdate, db: Session = Depends(get_db)):
    job = _get_job_or_404(db, job_id)
    updates = payload.model_dump(exclude_unset=True)
    if "job_url" in updates and updates["job_url"] is not None:
        updates["job_url"] = str(updates["job_url"])
    if "salary_min" in updates and "salary_max" not in updates and job.salary_max is not None:
        if updates["salary_min"] is not None and updates["salary_min"] > job.salary_max:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="salary_min cannot be greater than salary_max",
            )
    if "salary_max" in updates and "salary_min" not in updates and job.salary_min is not None:
        if updates["salary_max"] is not None and updates["salary_max"] < job.salary_min:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="salary_max cannot be less than salary_min",
            )
    for key, value in updates.items():
        setattr(job, key, value)
    db.commit()
    db.refresh(job)
    return ApiResponse(data=job, message="Job application updated")


@router.delete("/jobs/{job_id}", response_model=ApiResponse[dict])
def delete_job(job_id: UUID, db: Session = Depends(get_db)):
    job = _get_job_or_404(db, job_id)
    db.delete(job)
    db.commit()
    return ApiResponse(data={"id": str(job_id)}, message="Job application deleted")


@router.get("/stats", response_model=ApiResponse[Stats])
def get_stats(date_range: DateRange = Query(default="all"), db: Session = Depends(get_db)):
    stmt = select(Job)
    cutoff = _date_cutoff(date_range)
    if cutoff:
        stmt = stmt.where(Job.date_applied >= cutoff)
    jobs = db.scalars(stmt).all()

    by_status = {status.value: 0 for status in JobStatus}
    by_company: dict[str, int] = {}
    for job in jobs:
        by_status[job.status.value] += 1
        by_company[job.company] = by_company.get(job.company, 0) + 1

    stats = Stats(
        total_applications=len(jobs),
        interviews=by_status[JobStatus.INTERVIEW.value],
        rejections=by_status[JobStatus.REJECTED.value],
        pending=by_status[JobStatus.APPLIED.value],
        by_status=by_status,
        by_company=dict(sorted(by_company.items(), key=lambda item: item[1], reverse=True)[:10]),
    )
    return ApiResponse(data=stats)
