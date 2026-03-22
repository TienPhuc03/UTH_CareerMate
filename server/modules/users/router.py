from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core import security
from core.dependencies import get_current_user
from database.session import get_db
from modules.users import curd, schemas
from modules.users.roles import normalize_user_role

router = APIRouter()

DbDependency = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: DbDependency):
    """Register a new user."""
    existing_user = curd.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email da duoc su dung",
        )

    return curd.create_user(
        db=db,
        email=user.email,
        full_name=user.full_name,
        password=user.password,
        role=user.role,
    )


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: DbDependency):
    """Login user and return access token."""
    db_user = curd.get_user_by_email(db, user.email)
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoac mat khau khong chinh xac",
        )

    access_token = security.create_access_token(data={"sub": db_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": normalize_user_role(db_user.role) or "candidate",
        "email": db_user.email,
    }


@router.get("/profile", response_model=schemas.UserOut)
def get_profile(current_user=Depends(get_current_user)):
    return current_user
