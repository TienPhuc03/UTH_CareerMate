from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from modules.users.auth import get_current_user
from modules.users.model import User
from .middleware import require_recruiter
from modules.jobs.model import Job
from modules.applications.model import Application

router = APIRouter()

@router.post("/jobs")
def create_job(data: dict, db: Session = Depends(get_db), current_user: User = Depends(require_recruiter)):
    new_job = Job(**data, recruiter_id=current_user.id)
    db.add(new_job)
    db.commit()
    return {"message": "Đăng tin thành công"}

@router.get("/applications/{job_id}")
def get_job_applications(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_recruiter)):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy công việc")
    
    apps = db.query(Application).filter(Application.job_id == job_id).all()
    return apps