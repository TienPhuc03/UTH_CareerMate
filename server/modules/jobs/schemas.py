from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


JobStatus = Literal["active", "closed", "draft"]
JobType = Literal["full_time", "part_time", "internship", "remote"]


class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: JobType = "full_time"
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    location: Optional[str] = None
    company_name: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    status: JobStatus = "active"
    expires_at: Optional[datetime] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[JobType] = None
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    location: Optional[str] = None
    company_name: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    status: Optional[JobStatus] = None
    expires_at: Optional[datetime] = None


class JobResponse(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recruiter_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_approved: bool = True
