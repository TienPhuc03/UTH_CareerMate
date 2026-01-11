#api nhận file pdf/docsx từ user, trích xuất thông tin và lưu vào db
#api trả về kết quả phân tích 
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database.session import get_db
from modules.cvs.schemas import CVCreate, CVResponse
from modules.cvs.service import create_cv, get_all_cvs

router = APIRouter()

@router.post("/", response_model=CVResponse)
def upload_cv(cv: CVCreate, db: Session = Depends(get_db)):
    return create_cv(db, cv)

@router.get("/", response_model=List[CVResponse])
def list_cvs(db: Session = Depends(get_db)):
    return get_all_cvs(db)
