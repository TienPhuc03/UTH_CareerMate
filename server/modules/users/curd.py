# # hàm để lưu thông tin (đại học, chuyên ngành, gpa,...) của user vào database
# # crud.py
# from sqlalchemy.orm import Session
# from modules.users import model
# from core.security import get_password_hash
# from pydantic import SecretStr


# def get_user_by_email(db: Session, email: str):
#     return db.query(model.User).filter(model.User.email == email).first()

# def create_user (db: Session, email: str , full_name: str, password: str):
#     hashed_password = get_password_hash(password)
#     user = model.User(
#         email=email,
#         full_name=full_name,
#         hashed_password=hashed_password
#     )
#     print("Creating user:", user)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user
from sqlalchemy.orm import Session
from modules.users.model import User
from core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, email: str, full_name: str, password: str):
    """Create a new user"""
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user