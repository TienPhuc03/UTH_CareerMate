from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database.base import get_db
from modules.users.models import User
from modules.jobs.models import Job
from modules.applications.models import Application
from core.dependencies import require_admin
from . import analytics

# Global Admin Protection
router = APIRouter(
    prefix="/admin", 
    tags=["Admin"], 
    dependencies=[Depends(require_admin)]
)

# DASHBOARD

@router.get("/dashboard/stats")
def read_dashboard_stats(db: Session = Depends(get_db)):
    """Get comprehensive dashboard statistics"""
    return analytics.get_dashboard_stats(db)


# USER MANAGEMENT

@router.get("/users")
def list_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    role: Optional[str] = Query(None),          # Filter by role
    status: Optional[str] = Query(None),        # active, inactive
    search: Optional[str] = Query(None),        # Search by email/name
    db: Session = Depends(get_db)
):
    query = db.query(User)
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
    if status:
        if status.lower() == "active":
            query = query.filter(User.is_active == True)
        elif status.lower() == "inactive":
            query = query.filter(User.is_active == False)
    
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) | 
            (User.full_name.ilike(f"%{search}%"))
        )
    
    total = query.count()
    total_pages = (total + limit - 1) // limit
    users = query.offset((page-1)*limit).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": total_pages,
        "users": users
    }

@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db)
):
    """Update user active/inactive status"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "is_active": is_active,
        "message": "Cập nhật trạng thái thành công"
    }

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    user_email = user.email
    
    # Delete related data
    if user.role == "recruiter":
        jobs = db.query(Job).filter(Job.recruiter_id == user_id).all()
        for job in jobs:
            applications = db.query(Application).filter(Application.job_id == job.id).all()
            for app in applications:
                db.delete(app)
            db.delete(job)
    
    # Delete applications by this user
    applications = db.query(Application).filter(Application.candidate_id == user_id).all()
    for app in applications:
        db.delete(app)
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return {
        "id": user_id,
        "email": user_email,
        "message": f"Đã xóa user '{user_email}' và dữ liệu liên quan"
    }

# JOB MANAGEMENT

@router.get("/jobs")
def list_all_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),      # Filter: active, closed
    company: Optional[str] = Query(None),     # Filter: company name
    date_from: Optional[str] = Query(None),   # Filter: từ ngày (YYYY-MM-DD)
    date_to: Optional[str] = Query(None),     # Filter: đến ngày (YYYY-MM-DD)
    db: Session = Depends(get_db)
):
    # Base query
    query = db.query(Job)
    
    # Apply filters
    if status:
        if status.lower() == "active":
            query = query.filter(Job.is_active == True)
        elif status.lower() == "closed":
            query = query.filter(Job.is_active == False)
    
    if company:
        query = query.filter(Job.title.contains(company))
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Job.created_at >= from_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, "%Y-%m-%d")
            query = query.filter(Job.created_at <= to_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    jobs = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "total": total,
        "jobs": jobs
    }

@router.get("/jobs/{job_id}")
def get_job_detail(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job

@router.put("/jobs/{job_id}/status")
def update_job_status(
    job_id: int,
    is_active: bool,
    db: Session = Depends(get_db)
):
    """Update job active/inactive status"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    old_status = job.is_active
    job.is_active = is_active
    db.commit()
    db.refresh(job)
    
    action = "activated" if is_active else "deactivated"
    
    return {
        "id": job.id,
        "title": job.title,
        "status": "active" if job.is_active else "closed",
        "message": f"Job {action} successfully"
    }

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Find job
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    # Check if job has applications
    app_count = db.query(Application).filter(Application.job_id == job_id).count()
    
    if app_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete. {app_count} applications exist for this job"
        )
    # Delete job
    job_title = job.title
    db.delete(job)
    db.commit()
    
    return {
        "id": job_id,
        "title": job_title,
        "message": f"Job '{job_title}' deleted successfully"
    }