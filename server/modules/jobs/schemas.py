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
    company_name: Optional[str] = None
    requirements: Optional[str] = None  # Thêm field này
    benefits: Optional[str] = None      # Thêm field này  # Thêm field này để FE gửi lên
    status: Optional[str] = None        
    expires_at: Optional[datetime] = None 


class JobResponse(JobCreate):
    id: int
    recruiter_id: int               # FE cần biết ai đăng
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str                     # FE cần biết tin đang đóng hay mở
    expires_at: Optional[datetime] = None 

    class Config:
        from_attributes = True
