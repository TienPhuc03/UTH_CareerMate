from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db #
from . import schemas, models

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/", response_model=List[schemas.JobResponse])
def search_jobs(keyword: str = "", db: Session = Depends(get_db)):
    # UC 23: Search for jobs
    return db.query(models.Job).filter(models.Job.title.contains(keyword)).all()

@router.post("/", response_model=schemas.JobResponse)
def post_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    # UC 30: Post Job Openings (Recruiter)
    db_job = models.Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job