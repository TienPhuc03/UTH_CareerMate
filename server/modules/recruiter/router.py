from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional
from datetime import datetime

from database.session import get_db
from modules.users.models import User
from modules.jobs.models import Job
from modules.applications.models import Application
from modules.jobs.schemas import JobCreate, JobUpdate, JobResponse
from core.dependencies import require_recruiter

router = APIRouter(
    tags=["Recruiter"],
    dependencies=[Depends(require_recruiter)]
)

# =======================
# DASHBOARD STATS (Tối ưu hóa query)
# =======================

@router.get("/stats")
def get_recruiter_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """
    Thống kê tổng hợp cho Recruiter (Optimized với 2 queries hiệu quả)
    """
    # Tối ưu: Dùng 1 query với conditional aggregation cho Jobs
    job_stats = db.query(
        func.count(Job.id).label("total_jobs"),
        func.sum(case((Job.status == "active", 1), else_=0)).label("active_jobs"),
        func.sum(case((Job.status == "closed", 1), else_=0)).label("closed_jobs"),
        func.sum(case((Job.status == "draft", 1), else_=0)).label("draft_jobs")
    ).filter(Job.recruiter_id == current_user.id).first()
    
    # Query riêng cho Applications với GROUP BY để breakdown theo status
    app_stats_raw = db.query(
        Application.status,
        func.count(Application.id).label("count")
    ).join(Job).filter(
        Job.recruiter_id == current_user.id
    ).group_by(Application.status).all()
    
    # Convert sang dict để dễ access
    app_breakdown = {status: count for status, count in app_stats_raw}
    total_applications = sum(app_breakdown.values())

    return {
        "jobs": {
            "total": job_stats.total_jobs or 0,
            "active": job_stats.active_jobs or 0,
            "closed": job_stats.closed_jobs or 0,
            "draft": job_stats.draft_jobs or 0
        },
        "applications": {
            "total": total_applications,
            "pending": app_breakdown.get("PENDING", 0),
            "reviewing": app_breakdown.get("REVIEWING", 0),
            "interviewed": app_breakdown.get("INTERVIEWED", 0),
            "accepted": app_breakdown.get("ACCEPTED", 0),
            "rejected": app_breakdown.get("REJECTED", 0)
        }
    }

# =======================
# JOB MANAGEMENT
# =======================

@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """Đăng tin tuyển dụng mới với validation nâng cao"""
    
    # Validation: Kiểm tra salary
    if job_data.salary_min and job_data.salary_max:
        if job_data.salary_min > job_data.salary_max:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="salary_min must be less than salary_max"
            )
    
    # Validation: Expires date phải trong tương lai
    if job_data.expires_at and job_data.expires_at <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expires_at must be a future date"
        )
    
    # Tạo Job
    new_job = Job(
        recruiter_id=current_user.id,
        recruiter_email=current_user.email,
        
        title=job_data.title,
        description=job_data.description,
        salary_range=job_data.salary_range,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        job_type=job_data.job_type,
        location=job_data.location,
        company_name=job_data.company_name or "Unknown Company",
        requirements=job_data.requirements,
        benefits=job_data.benefits,
        status=job_data.status or "active",
        expires_at=job_data.expires_at
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job

@router.get("/jobs", response_model=List[JobResponse])
def get_my_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, regex="^(active|closed|draft)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """
    Lấy danh sách Job với pagination và filter
    - skip: Bỏ qua n records đầu
    - limit: Tối đa n records (max 100)
    - status_filter: Lọc theo status
    """
    query = db.query(Job).filter(Job.recruiter_id == current_user.id)
    
    if status_filter:
        query = query.filter(Job.status == status_filter)
    
    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_detail(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """Xem chi tiết Job (Authorization check)"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or unauthorized"
        )
        
    return job

@router.put("/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """Cập nhật Job với validation"""
    job = db.query(Job).filter(
        Job.id == job_id, 
        Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Validation cho update
    update_data = job_update.dict(exclude_unset=True)
    
    # Check salary nếu đang update
    new_min = update_data.get("salary_min", job.salary_min)
    new_max = update_data.get("salary_max", job.salary_max)
    if new_min and new_max and new_min > new_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="salary_min cannot exceed salary_max"
        )
    
    # Apply updates
    for key, value in update_data.items():
        setattr(job, key, value)
        
    db.commit()
    db.refresh(job)
    return job

@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter)
):
    """
    Xóa Job (Cân nhắc soft delete thay vì hard delete)
    """
    job = db.query(Job).filter(
        Job.id == job_id, 
        Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check xem có applications nào chưa - Cảnh báo
    app_count = db.query(func.count(Application.id)).filter(
        Application.job_id == job_id
    ).scalar()
    
    if app_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete job with {app_count} existing applications. Consider closing it instead."
        )
        
    db.delete(job)
    db.commit()
    return None  # 204 No Content


