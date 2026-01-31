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
<<<<<<< HEAD
    user_id: Optional[int] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    ats_score: Optional[float] = None
    ai_feedback: Optional[dict] = None
=======
    user_id: Optional[int] = None    
    
    # File Info
    file_path: Optional[str] = None  
    file_name: Optional[str] = None  
    file_type: Optional[str] = None
    
    # AI Results
    ats_score: Optional[float] = None       
    ai_feedback: Optional[Dict[str, Any]] = None 
    
>>>>>>> 7962ebe50e2ff639a687f226a5b3309534e301f1
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
