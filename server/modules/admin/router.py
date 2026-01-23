from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database.base import get_db  
from modules.users.models import User
from . import analytics
from core.dependencies import require_admin

# Global Admin Protection
router = APIRouter(
    prefix="/admin", 
    tags=["Admin"], 
    dependencies=[Depends(require_admin)]
)

@router.get("/dashboard/stats")
def read_dashboard_stats(db: Session = Depends(get_db)):
    return analytics.get_dashboard_stats(db)

@router.get("/users")
def list_all_users(
    page: int = 1, 
    limit: int = 10, 
    search: str = None, 
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if search:
        query = query.filter(User.full_name.contains(search))
    
    total = query.count()
    users = query.offset((page-1)*limit).limit(limit).all()
    return {"total": total, "users": users}

@router.put("/users/{user_id}/status")
def update_user_status(user_id: int, is_active: bool, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    return {"message": "Cập nhật trạng thái thành công"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "Đã xóa user và dữ liệu liên quan"}