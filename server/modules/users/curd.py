from sqlalchemy.orm import Session

from core.security import get_password_hash
from modules.users.models import User
from modules.users.roles import normalize_user_role


def get_user_by_email(db: Session, email: str):
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, email: str, full_name: str, password: str | None, role: str = "candidate"):
    # Nếu user Google (password=None) thì không hash
    hashed_password = get_password_hash(password) if password else None

    db_user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=normalize_user_role(role) or "candidate",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
