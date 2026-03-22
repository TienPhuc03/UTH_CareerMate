from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_recruiter
from database.session import get_db
from modules.applications import crud, schemas
from modules.users.models import User

router = APIRouter(tags=["Applications"])


@router.post("/apply", response_model=schemas.ApplicationResponse)
def submit_application(
    app_in: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.apply_for_job(db, app_in, current_user.id)


@router.get("/get", response_model=list[schemas.ApplicationResponse])
def list_all_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    return crud.get_applications_for_recruiter(db, current_user.id)


@router.patch("/{app_id}/status", response_model=schemas.ApplicationResponse)
def update_status(
    app_id: int,
    app_update: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    updated_app = crud.update_status(db, app_id, current_user.id, app_update.status)
    if not updated_app:
        raise HTTPException(status_code=404, detail="Khong tim thay don")
    return updated_app
