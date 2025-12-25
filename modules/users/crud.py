from sqlalchemy.orm import Session
from . import models, security

# Hàm tạo người dùng mới (Dùng cho đăng ký tài khoản)
def create_user(db: Session, email: str, password: str, full_name: str):
    hashed_password = security.hash_password(password)
    db_user = models.User(
        email=email, 
        hashed_password=hashed_password, 
        full_name=full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Hàm tìm người dùng theo Email (Dùng cho Đăng nhập)
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Hàm lấy thông tin người dùng theo ID
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()