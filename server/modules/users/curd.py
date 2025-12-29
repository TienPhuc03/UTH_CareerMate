# hàm để lưu thông tin (đại học, chuyên ngành, gpa,...) của user vào database
# crud.py
from sqlalchemy.orm import Session
from modules.users import model
from core.security import get_password_hash


def get_user_by_email(db: Session, email: str):
    return db.query(model.User).filter(model.User.email == email).first()

def create_user (db: Session, email: str , full_name: str, password: str):
    hashed_password = get_password_hash(password)
    user = model.User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
