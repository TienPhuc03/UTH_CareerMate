from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from core.dependencies import get_current_user
from modules.users.models import User
from modules.jobs.models import Job
from modules.applications.models import Application
from modules.admin.middleware import require_admin as require_recruiter

router = APIRouter()

@router.post("/jobs")
def create_job(data: dict, db: Session = Depends(get_db), current_user: User = Depends(require_recruiter)):
    new_job = Job(**data, recruiter_id=current_user.id)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return {"message": "Đăng tin thành công", "job_id": new_job.id}

@router.get("/applications/{job_id}")
def get_job_applications(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_recruiter)):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy công việc")
    
    apps = db.query(Application).filter(Application.job_id == job_id).all()
    return apps