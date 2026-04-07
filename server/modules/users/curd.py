from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from core.security import get_password_hash, is_expired, utc_now
from modules.users.models import User, UserSession
from modules.users.roles import normalize_user_role


def get_user_by_email(db: Session, email: str):
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    email: str,
    full_name: str,
    password: str | None,
    role: str = "candidate",
):
    """Create a local or Google-authenticated user."""
    hashed_password = get_password_hash(password) if password else None

    db_user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        role=normalize_user_role(role) or "candidate",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def cleanup_expired_sessions(db: Session, now: datetime | None = None) -> int:
    """Delete expired sessions to keep the session table tidy."""
    current_time = now or utc_now()
    deleted = (
        db.query(UserSession)
        .filter(UserSession.expires_at.is_not(None))
        .filter(UserSession.expires_at <= current_time)
        .delete(synchronize_session=False)
    )
    if deleted:
        db.commit()
    return deleted


def create_user_session(
    db: Session,
    user_id: int,
    jti: str,
    expires_at: datetime,
) -> UserSession:
    """Persist a server-side session for a newly issued token."""
    db_session = UserSession(
        user_id=user_id,
        token=jti,
        expires_at=expires_at,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_active_session_by_jti(
    db: Session,
    jti: str,
    now: datetime | None = None,
) -> UserSession | None:
    """Return the active session associated with a token identifier."""
    current_time = now or utc_now()
    session = (
        db.query(UserSession)
        .filter(UserSession.token == jti)
        .filter(
            or_(
                UserSession.expires_at.is_(None),
                UserSession.expires_at > current_time,
            )
        )
        .first()
    )

    if session and session.expires_at and is_expired(session.expires_at, current_time):
        delete_session_by_jti(db, jti)
        return None

    return session


def delete_session_by_jti(db: Session, jti: str) -> bool:
    """Delete a session by token identifier."""
    deleted = (
        db.query(UserSession)
        .filter(UserSession.token == jti)
        .delete(synchronize_session=False)
    )
    if deleted:
        db.commit()
    return bool(deleted)
