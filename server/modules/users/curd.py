from sqlalchemy.orm import Session
# Phải import User từ file model cùng thư mục
from server.modules.users.model import User 
from server.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    # Dùng trực tiếp User thay vì model.User
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, full_name: str, password: str):
    hashed_password = get_password_hash(password)
    new_user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user