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
    status: str
    applied_at: datetime

    class Config:
        from_attributes = True
        