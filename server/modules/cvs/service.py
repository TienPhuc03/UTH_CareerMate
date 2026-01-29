#hàm tính điểm khớp giữa yêu cầu công việc và kỹ năng trong CV
from sqlalchemy.orm import Session
from .models import CV
from .schemas import CVCreate
from .utils import normalize_text
from typing import Optional, Dict, Any

def create_cv(
    db: Session, 
    cv_data: CVCreate, 
    user_id: Optional[int] = None,
    file_path: Optional[str] = None, 
    file_name: Optional[str] = None,
    file_type: Optional[str] = None,
    ats_score: Optional[float] = None, 
    ai_feedback: Optional[Dict[str, Any]] = None
):
    cv = CV(
        full_name=cv_data.full_name,
        email=cv_data.email,
        phone=cv_data.phone,
        skills=normalize_text(cv_data.skills) if cv_data.skills else None,
        experience=normalize_text(cv_data.experience) if cv_data.experience else None,
        education=normalize_text(cv_data.education) if cv_data.education else None, 
        
        user_id=user_id,
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        ats_score=ats_score,
        ai_feedback=ai_feedback
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return cv
