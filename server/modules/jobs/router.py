from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.jobs.models import Job
from modules.jobs.schemas import JobCreate, JobResponse
from core.dependencies import require_recruiter
from modules.users.models import User

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    job_data = job.dict()
    # Tự động gán thông tin recruiter
    job_data["recruiter_id"] = current_user.id
    job_data["recruiter_email"] = current_user.email
    
    # Nếu FE không gửi company_name, có thể để null hoặc lấy từ profile (nếu có)
    # Hiện tại cứ lưu nguyên trạng
    
    new_job = Job(**job_data)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()
