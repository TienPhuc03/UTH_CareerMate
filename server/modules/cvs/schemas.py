from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

class CVCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None  

class CVResponse(CVCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    ats_score: Optional[float] = None
    ai_feedback: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

