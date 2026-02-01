#api nộp đơn (ứng viện A sẽ nộp vào job B)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from modules.applications import crud
from modules.applications import schemas
from core.dependencies import get_current_user

router = APIRouter(tags=["Applications"])

@router.post("/apply", response_model=schemas.ApplicationResponse)
def submit_application(
    app_in: schemas.ApplicationCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # Lấy thông tin người dùng hiện tại
):
    # Gọi crud với user_id lấy từ token
    return crud.apply_for_job(db, app_in, current_user.id)


@router.get("/get", response_model=list[schemas.ApplicationResponse])
def list_all_applications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Chỉ trả về những đơn ứng tuyển thuộc các Job của recruiter này
    return crud.get_applications_for_recruiter(db, current_user.id)

@router.patch("/{app_id}/status", response_model=schemas.ApplicationResponse)
def update_status(
    app_id: int, 
    app_update: schemas.ApplicationUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # SỬA: Đổi tên hàm thành update_status cho khớp với crud.py
    updated_app = crud.update_status(db, app_id, app_update.status)
    if not updated_app:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn")
    return updated_app