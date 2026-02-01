from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ApplicationCreate(BaseModel):
    job_id: int
    cv_id: int
    cover_letter: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    cv_id: int
    user_id: Optional[int]
    status: str
    created_at: datetime
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    job_title: Optional[str] = None

    class Config:
        from_attributes = True

class ApplicationUpdate(BaseModel):
    status: str