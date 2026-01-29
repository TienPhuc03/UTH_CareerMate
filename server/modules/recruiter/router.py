from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.session import get_db
from modules.users.models import User
from modules.jobs.models import Job
from modules.jobs.schemas import JobCreate, JobUpdate, JobResponse
from core.dependencies import require_recruiter

# Router cho Recruiter (Prefix /api/recruiter đã khai báo ở main.py)
router = APIRouter(
    tags=["Recruiter"],
    dependencies=[Depends(require_recruiter)]
)

# =======================
# JOB MANAGEMENT
# =======================

@router.post("/jobs", response_model=JobResponse)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """Đăng tin tuyển dụng mới"""
    
    # Xử lý company_name nếu thiếu
    company = job_data.company_name
    if not company:
        company = "Unknown Company"

    # Tạo Job theo form cũ (Liệt kê từng trường để dễ kiểm soát)
    new_job = Job(
        recruiter_id=current_user.id,
        recruiter_email=current_user.email,
        
        # Job Info
        title=job_data.title,
        description=job_data.description,
        
        # Details & Salary (Các trường mới)
        salary_range=job_data.salary_range,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        job_type=job_data.job_type,
        
        # Location & Company
        location=job_data.location,  # Đã fix lỗi lặp location ở đây
        company_name=company,
        
        # Requirements & Benefits
        requirements=job_data.requirements,
        benefits=job_data.benefits,
        
        # Meta
        status=job_data.status or "active",
        expires_at=job_data.expires_at
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job

@router.get("/jobs", response_model=List[JobResponse])
def get_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """Lấy danh sách Job của chính Recruiter này"""
    jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_detail(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """Xem chi tiết Job (Chỉ xem được Job của mình)"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return job

@router.put("/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """Cập nhật Job"""
    job = db.query(Job).filter(
        Job.id == job_id, 
        Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Ở đây dùng exclude_unset=True để chỉ update những trường người dùng gửi lên
    
    update_data = job_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)
        
    db.commit()
    db.refresh(job)
    return job

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """Xóa Job"""
    job = db.query(Job).filter(
        Job.id == job_id, 
        Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}