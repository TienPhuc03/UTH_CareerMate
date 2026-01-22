#Chặn các account không phải nhà tuyển dụng (admin & recruiter)
from fastapi import HTTPException, Depends
from modules.users.models import User
from core.dependencies import get_current_user 

def require_recruiter(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Quyền truy cập bị từ chối")
    return current_user