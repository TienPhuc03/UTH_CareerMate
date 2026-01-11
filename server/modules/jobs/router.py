from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.jobs.models import Job
from modules.jobs.schemas import JobCreate, JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = Job(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()
