#hàm tính điểm khớp giữa yêu cầu công việc và kỹ năng trong CV
from sqlalchemy.orm import Session
from .models import CV
from .schemas import CVCreate
from .utils import normalize_text

def create_cv(db: Session, cv_data: CVCreate):
    cv = CV(
        full_name=cv_data.full_name,
        email=cv_data.email,
        phone=cv_data.phone,
        skills=normalize_text(cv_data.skills) if cv_data.skills else None,
        experience=normalize_text(cv_data.experience) if cv_data.experience else None
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return cv

def get_all_cvs(db: Session):
    return db.query(CV).all()
