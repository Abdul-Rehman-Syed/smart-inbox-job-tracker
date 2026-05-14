from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, model_validator

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


class JobStatusHistoryRead(BaseModel):
    id: UUID
    job_id: UUID
    old_status: Optional[str] = None
    new_status: str
    source: str
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobRead(JobBase):
    id: UUID
    user_id: UUID
    job_url: str
    created_at: datetime
    updated_at: datetime
    status_history: list[JobStatusHistoryRead] = Field(default_factory=list)

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


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=160)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


ApiData = Dict[str, Any]
