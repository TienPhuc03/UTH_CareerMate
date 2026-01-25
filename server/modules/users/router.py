
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from modules.users import schemas, curd
from core import security
from database.session import get_db
from core.dependencies import get_current_user

router = APIRouter()

# Type alias for database dependency
DbDependency = Annotated[Session, Depends(get_db)]

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: DbDependency):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = curd.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    
    # Create new user
    new_user = curd.create_user(
        db=db,
        email=user.email,
        full_name=user.full_name,
        password=user.password
    )
    
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: DbDependency):
    """
    Login user and return access token
    """
    # Verify user credentials
    db_user = curd.get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    
    if not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    
    # Create access token
    access_token = security.create_access_token(
        data={"sub": db_user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/profile")
def get_profile(current_user = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role}