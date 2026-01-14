
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
