from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


ApplicationStatus = Literal["PENDING", "REVIEWING", "INTERVIEWED", "ACCEPTED", "REJECTED"]


class ApplicationCreate(BaseModel):
    job_id: int
    cv_id: int
    cover_letter: Optional[str] = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    cv_id: int
    user_id: int
    status: ApplicationStatus
    created_at: datetime
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    job_title: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus
