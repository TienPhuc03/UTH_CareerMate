# 
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CVCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None

class CVResponse(CVCreate):
    id: int
    user_id: Optional[int] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    ats_score: Optional[float] = None
    ai_feedback: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
