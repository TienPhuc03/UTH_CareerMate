from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db

router = APIRouter(prefix="/users", tags=["Users Management"])

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return {"message": "Danh sách người dùng sẽ hiển thị ở đây"}