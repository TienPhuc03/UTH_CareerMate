# 
from pydantic import BaseModel, EmailStr
from typing import Any, Dict, Optional
from datetime import datetime

class CVCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None  

class CVResponse(CVCreate):
    id: int
    user_id: Optional[int] = None    
    
    # File Info
    file_path: Optional[str] = None  
    file_name: Optional[str] = None  
    file_type: Optional[str] = None
    
    # AI Results
    ats_score: Optional[float] = None       
    ai_feedback: Optional[Dict[str, Any]] = None 
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
