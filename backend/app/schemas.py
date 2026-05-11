from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.models import JobStatus


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    message: str | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    data: None = None
    message: str


class JobBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=160)
    job_title: str = Field(..., min_length=1, max_length=200)
    job_url: HttpUrl
    date_applied: datetime
    status: JobStatus = JobStatus.APPLIED
    salary_min: Optional[Decimal] = Field(default=None, ge=0)
    salary_max: Optional[Decimal] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_min > self.salary_max:
            raise ValueError("salary_min cannot be greater than salary_max")
        return self


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    company: Optional[str] = Field(default=None, min_length=1, max_length=160)
    job_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    job_url: Optional[HttpUrl] = None
    date_applied: Optional[datetime] = None
    status: Optional[JobStatus] = None
    salary_min: Optional[Decimal] = Field(default=None, ge=0)
    salary_max: Optional[Decimal] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_min > self.salary_max:
            raise ValueError("salary_min cannot be greater than salary_max")
        return self


class JobRead(JobBase):
    id: UUID
    job_url: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Stats(BaseModel):
    total_applications: int
    interviews: int
    rejections: int
    pending: int
    by_status: Dict[str, int]
    by_company: Dict[str, int]


class Health(BaseModel):
    status: str
    environment: str
    database: str


ApiData = Dict[str, Any]
