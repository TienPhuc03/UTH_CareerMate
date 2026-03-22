from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import require_recruiter
from database.session import get_db
from modules.jobs.models import Job
from modules.jobs.schemas import JobCreate, JobResponse
from modules.users.models import User

router = APIRouter()


@router.post("/up", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    if (
        job.salary_min is not None
        and job.salary_max is not None
        and job.salary_min > job.salary_max
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="salary_min cannot exceed salary_max",
        )

    job_payload = job.model_dump()
    if not job_payload.get("company_name"):
        job_payload["company_name"] = "Unknown Company"

    new_job = Job(
        **job_payload,
        recruiter_id=current_user.id,
        recruiter_email=current_user.email,
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@router.get("/get", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).all()
