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
    created_at: datetime

    class Config:
        from_attributes = True
