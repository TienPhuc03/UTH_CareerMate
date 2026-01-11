from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: str = "full_time"

class JobResponse(JobCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
