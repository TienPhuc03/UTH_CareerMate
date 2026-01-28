from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.dependencies import get_db
from core.dependencies import require_recruiter
from modules.users.models import User
from modules.jobs.models import Job
from modules.applications.models import Application
from modules.jobs.schemas import JobResponse, JobCreate, JobUpdate
from modules.applications.schemas import ApplicationResponse

router = APIRouter(prefix="/api/recruiter", tags=["Recruiter"])

# Type alias
DbDependency = Session

#HELPER FUNCTIONS

def check_job_ownership(job_id: int, current_user: User, db: DbDependency) -> Job:
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check ownership: recruiter must own job OR be admin
    if job.recruiter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your job"
        )
    
    return job

def check_application_ownership(application_id: int, current_user: User, db: DbDependency) -> Application:
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get job and check ownership
    job = db.query(Job).filter(Job.id == application.job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.recruiter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your application"
        )
    
    return application


#MY JOBS ENDPOINTS 

@router.get("/jobs", response_model=List[JobResponse])
def get_my_jobs(
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    if current_user.role == "admin":
        # Admin can see all jobs
        jobs = db.query(Job).all()
    else:
        # Recruiter can only see their own jobs
        jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
    
    return jobs
# oke

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_detail(
    job_id: int,
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    job = check_job_ownership(job_id, current_user, db)
    return job


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    new_job = Job(
        title=job_data.title,
        description=job_data.description,
        recruiter_id=current_user.id,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        location=job_data.location,
        is_active=True
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job


@router.put("/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    job = check_job_ownership(job_id, current_user, db)
    
    # Update fields
    if job_data.title:
        job.title = job_data.title
    if job_data.description:
        job.description = job_data.description
    if job_data.salary_min is not None:
        job.salary_min = job_data.salary_min
    if job_data.salary_max is not None:
        job.salary_max = job_data.salary_max
    if job_data.location:
        job.location = job_data.location
    
    db.commit()
    db.refresh(job)
    
    return job


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    job = check_job_ownership(job_id, current_user, db)
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}


#APPLICATIONS ENDPOINTS 

@router.get("/jobs/{job_id}/applications", response_model=List[ApplicationResponse])
def get_job_applications(
    job_id: int,
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    # Check job ownership
    job = check_job_ownership(job_id, current_user, db)
    
    # Get applications for this job
    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).all()
    
    return applications


@router.get("/applications", response_model=List[ApplicationResponse])
def get_all_my_applications(
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    if current_user.role == "admin":
        # Admin sees all applications
        applications = db.query(Application).all()
    else:
        # Recruiter sees applications for their jobs only
        recruiter_jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
        job_ids = [job.id for job in recruiter_jobs]
        
        applications = db.query(Application).filter(
            Application.job_id.in_(job_ids)
        ).all()
    
    return applications


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application_detail(
    application_id: int,
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    application = check_application_ownership(application_id, current_user, db)
    return application


@router.put("/applications/{application_id}/status")
def update_application_status(
    application_id: int,
    new_status: str,
    notes: Optional[str] = None,
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    # Check ownership
    application = check_application_ownership(application_id, current_user, db)
    
    # Valid statuses
    valid_statuses = ["PENDING", "REVIEWING", "INTERVIEWED", "ACCEPTED", "REJECTED"]
    
    if new_status.upper() not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Validate status transitions
    valid_transitions = {
        "PENDING": ["REVIEWING", "REJECTED"],
        "REVIEWING": ["INTERVIEWED", "REJECTED", "PENDING"],
        "INTERVIEWED": ["ACCEPTED", "REJECTED"],
        "ACCEPTED": ["REJECTED"],
        "REJECTED": ["PENDING"]
    }
    
    current_status = application.status.upper()
    new_status = new_status.upper()
    
    if current_status not in valid_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Current status '{current_status}' is invalid"
        )
    
    if new_status not in valid_transitions[current_status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {current_status} to {new_status}"
        )
    
    # Update status
    application.status = new_status
    if notes:
        application.notes = notes
    
    db.commit()
    db.refresh(application)
    
    return {
        "id": application.id,
        "job_id": application.job_id,
        "candidate_id": application.candidate_id,
        "status": application.status,
        "notes": application.notes,
        "created_at": application.created_at,
        "updated_at": application.updated_at
    }


#STATISTICS ENDPOINTS 

@router.get("/stats")
def get_recruiter_stats(
    current_user: User = Depends(require_recruiter),
    db: DbDependency = Depends(get_db)
):
    if current_user.role == "admin":
        # Admin stats
        jobs = db.query(Job).all()
        applications = db.query(Application).all()
    else:
        # Recruiter stats - only their jobs
        jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
        job_ids = [job.id for job in jobs]
        applications = db.query(Application).filter(
            Application.job_id.in_(job_ids)
        ).all()
    
    # Calculate job stats
    total_jobs = len(jobs)
    active_jobs = len([j for j in jobs if j.is_active])
    closed_jobs = len([j for j in jobs if not j.is_active])
    
    # Calculate application stats
    total_apps = len(applications)
    pending_apps = len([a for a in applications if a.status.upper() == "PENDING"])
    reviewing_apps = len([a for a in applications if a.status.upper() == "REVIEWING"])
    interviewed_apps = len([a for a in applications if a.status.upper() == "INTERVIEWED"])
    accepted_apps = len([a for a in applications if a.status.upper() == "ACCEPTED"])
    rejected_apps = len([a for a in applications if a.status.upper() == "REJECTED"])
    
    return {
        "jobs": {
            "total": total_jobs,
            "active": active_jobs,
            "closed": closed_jobs
        },
        "applications": {
            "total": total_apps,
            "pending": pending_apps,
            "reviewing": reviewing_apps,
            "interviewed": interviewed_apps,
            "accepted": accepted_apps,
            "rejected": rejected_apps
        }
    }