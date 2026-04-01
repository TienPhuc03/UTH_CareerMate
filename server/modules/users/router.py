from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core import security
from core.config import settings
from core.dependencies import get_current_user
from database.session import get_db
from modules.users import curd, schemas
from modules.users.google_oauth import (
    exchange_code_for_token, 
    get_google_auth_url,
    get_google_user_info,
)
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

    access_token = security.create_access_token(
        data={
            "sub": db_user.email,
            "role": db_user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": normalize_user_role(db_user.role) or "candidate",
        "email": db_user.email,
    }


@router.get("/profile", response_model=schemas.UserOut)
def get_profile(current_user=Depends(get_current_user)):
    return current_user


@router.get("/google/login")
def google_login():
    """Redirect nguoi dung den trang dang nhap Google."""
    auth_url = get_google_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(db: DbDependency, code: str | None = None, error: str | None = None):
    """
    Google redirect ve day sau khi user dang nhap thanh cong.
    Doi code -> token -> user info -> tao/lay user -> tra JWT.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")

    token_data = await exchange_code_for_token(code)
    access_token_google = token_data.get("access_token")

    if not access_token_google:
        raise HTTPException(status_code=400, detail="Khong nhan duoc access token tu Google")

    google_user = await get_google_user_info(access_token_google)
    email = google_user.get("email")
    full_name = google_user.get("name", "")

    if not email:
        raise HTTPException(status_code=400, detail="Khong lay duoc email tu Google")

    db_user = curd.get_user_by_email(db, email)
    if not db_user:
        db_user = curd.create_user(
            db=db,
            email=email,
            full_name=full_name,
            password=None,
            role="candidate",
        )

    normalized_role = normalize_user_role(db_user.role) or "candidate"
    jwt_token = security.create_access_token(
        data={
            "sub": db_user.email,
            "role": normalized_role,
        }
    )

    query_string = urlencode(
        {
            "token": jwt_token,
            "email": email,
            "role": normalized_role,
        }
    )

    return RedirectResponse(
        url=f"{settings.GOOGLE_OAUTH_SUCCESS_REDIRECT_URL}?{query_string}"
    )
