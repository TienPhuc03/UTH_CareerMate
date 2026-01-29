#api nộp đơn (ứng viện A sẽ nộp vào job B)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from modules.applications import crud
from modules.applications import schemas

router = APIRouter(tags=["Applications"])

@router.post("/", response_model=schemas.ApplicationResponse)
def submit_application(app_in: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    return crud.apply_for_job(db, app_in)

@router.get("/", response_model=list[schemas.ApplicationResponse])
def list_all_applications(db: Session = Depends(get_db)):
    return crud.get_job_applications(db)