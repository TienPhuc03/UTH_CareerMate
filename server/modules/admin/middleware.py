from fastapi import HTTPException, status, Depends
# Lưu ý: Sửa lại đường dẫn import tùy theo cấu trúc folder của ông
from core.dependencies import get_current_user 

# Hàm này được router.py gọi để bảo vệ các route của Admin
def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này"
        )
    return current_user

def log_admin_action(admin_id: int, action: str):
    print(f"Admin {admin_id} performed: {action}")