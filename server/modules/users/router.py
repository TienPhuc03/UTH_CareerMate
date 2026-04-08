from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core.auth_rate_limit import LoginRateLimitStatus, login_rate_limiter
from core import security
from core.config import settings
from core.dependencies import AuthenticatedRequest, get_current_auth, get_current_user
from core.logging_config import get_logger
from database.session import get_db
from modules.users import curd, schemas
from modules.users.models import User
from modules.users.google_oauth import (
    decode_google_oauth_state,
    encode_google_oauth_state,
    exchange_code_for_token,
    get_google_auth_url,
    get_google_user_info,
    normalize_google_signup_role,
)
from modules.users.roles import normalize_user_role


router = APIRouter()
logger = get_logger(__name__)

DbDependency = Annotated[Session, Depends(get_db)]
AuthDependency = Annotated[AuthenticatedRequest, Depends(get_current_auth)]


def _build_token_response(db: Session, db_user: User) -> dict:
    """Issue a new access token and persist its server-side session."""
    normalized_role = normalize_user_role(db_user.role) or "candidate"
    curd.cleanup_expired_sessions(db)
    token_context = security.issue_access_token(
        data={
            "sub": db_user.email,
            "role": normalized_role,
        }
    )
    curd.create_user_session(
        db=db,
        user_id=db_user.id,
        jti=token_context.jti,
        expires_at=token_context.expires_at,
    )

    return {
        "access_token": token_context.token,
        "token_type": "bearer",
        "role": normalized_role,
        "email": db_user.email,
    }


def _raise_login_rate_limit(
    status_info: LoginRateLimitStatus,
    client_ip: str,
    email: str,
) -> None:
    retry_after = max(status_info.retry_after, 1)
    logger.warning(
        "Login rate limit exceeded for email=%s ip=%s retry_after=%s attempts=%s",
        email,
        client_ip,
        retry_after,
        status_info.attempts,
    )
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Qua nhieu lan dang nhap. Vui long thu lai sau {retry_after} giay.",
        headers={"Retry-After": str(retry_after)},
    )


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: DbDependency):
    """Register a new user."""
    normalized_role = normalize_user_role(user.role) or "candidate"
    if normalized_role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Khong the dang ky tai khoan admin tu endpoint cong khai",
        )

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
        role=normalized_role,
    )


@router.post("/login", response_model=schemas.Token)
def login(request: Request, user: schemas.UserLogin, db: DbDependency):
    """Login user and return access token."""
    normalized_email = login_rate_limiter.normalize_email(user.email)
    client_ip = login_rate_limiter.get_client_ip(request)

    rate_limit_status = login_rate_limiter.is_limited(client_ip, normalized_email)
    if rate_limit_status.limited:
        _raise_login_rate_limit(rate_limit_status, client_ip, normalized_email)

    db_user = curd.get_user_by_email(db, user.email)
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        failure_status = login_rate_limiter.record_failure(client_ip, normalized_email)
        if failure_status.limited:
            _raise_login_rate_limit(failure_status, client_ip, normalized_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoac mat khau khong chinh xac",
        )

    login_rate_limiter.reset(client_ip, normalized_email)
    return _build_token_response(db, db_user)


@router.post("/logout", response_model=schemas.MessageResponse)
def logout(auth: AuthDependency, db: DbDependency):
    """Logout the current session by revoking the current token's JTI."""
    session_jti = auth.session.token
    curd.cleanup_expired_sessions(db)
    curd.delete_session_by_jti(db, session_jti)
    return {"message": "Dang xuat thanh cong"}


@router.get("/profile", response_model=schemas.UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/google/login")
def google_login(role: str | None = None):
    """Redirect nguoi dung den trang dang nhap Google."""
    selected_role = normalize_google_signup_role(role)
    state = encode_google_oauth_state(selected_role)
    auth_url = get_google_auth_url(state=state)
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    db: DbDependency,
    code: str | None = None,
    error: str | None = None,
    state: str | None = None,
):
    """
    Google redirect ve day sau khi user dang nhap thanh cong.
    Doi code -> token -> user info -> tao/lay user -> tra JWT.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")

    selected_role = decode_google_oauth_state(state)
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
            role=selected_role,
        )

    token_response = _build_token_response(db, db_user)

    # Dùng fragment (#) thay vì query string (?)
    # Fragment không được gửi lên server, không xuất hiện trong server logs
    query_string = urlencode(
        {
            "token": token_response["access_token"],
            "email": email,
            "role": token_response["role"],
        }
    )

    return RedirectResponse(
        url=f"{settings.GOOGLE_OAUTH_SUCCESS_REDIRECT_URL}#{query_string}"
    )