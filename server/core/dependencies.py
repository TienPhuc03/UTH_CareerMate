from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from core import security
from database.session import get_db
from modules.users import curd
from modules.users.models import User, UserSession
from modules.users.roles import normalize_user_role


bearer_security = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedRequest:
    user: User
    session: UserSession
    token: str
    payload: dict


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_auth(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_security),
    db: Session = Depends(get_db),
) -> AuthenticatedRequest:
    """Authenticate the current bearer token against both JWT claims and DB session state."""
    if credentials is None:
        raise _unauthorized("Chua dang nhap, vui long cung cap token")

    token = credentials.credentials

    try:
        payload = security.decode_access_token(token)
    except JWTError as exc:
        raise _unauthorized("Token khong hop le hoac da het han") from exc

    email = payload.get("sub")
    jti = payload.get("jti")
    if not email or not jti:
        raise _unauthorized("Phien dang nhap khong hop le, vui long dang nhap lai")

    curd.cleanup_expired_sessions(db)

    user = curd.get_user_by_email(db, email)
    if user is None:
        raise _unauthorized("Khong tim thay tai khoan")

    if not user.is_active:
        raise _unauthorized("Tai khoan da bi vo hieu hoa")

    session = curd.get_active_session_by_jti(db, jti)
    if session is None or session.user_id != user.id:
        if session is not None and session.user_id != user.id:
            curd.delete_session_by_jti(db, jti)
        raise _unauthorized("Phien dang nhap da het hieu luc, vui long dang nhap lai")

    user.role = normalize_user_role(user.role) or "candidate"
    return AuthenticatedRequest(
        user=user,
        session=session,
        token=token,
        payload=payload,
    )


def get_current_user(auth: AuthenticatedRequest = Depends(get_current_auth)) -> User:
    return auth.user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yeu cau quyen Admin",
        )
    return current_user


def require_recruiter(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["admin", "recruiter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yeu cau quyen Recruiter hoac Admin",
        )
    return current_user
