from sqlalchemy.orm import Session
from .models import Application
from .schemas import ApplicationCreate

def apply_for_job(db: Session, app_data: ApplicationCreate):
    new_app = Application(
        job_id=app_data.job_id,
        cv_id=app_data.cv_id,
        cover_letter=app_data.cover_letter
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

def get_job_applications(db: Session):
    return db.query(Application).all()