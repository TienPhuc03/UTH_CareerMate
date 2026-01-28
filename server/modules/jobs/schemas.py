from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: str = "full_time"
    salary_min: Optional[float] = None      # ← Thêm các field này
    salary_max: Optional[float] = None      # ← vì router.py đang dùng
    location: Optional[str] = None   


class JobUpdate(BaseModel):                 
    title: Optional[str] = None
    description: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    location: Optional[str] = None


class JobResponse(JobCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
