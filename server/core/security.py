from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
from jose import jwt

from core.config import settings


@dataclass(frozen=True)
class AccessTokenContext:
    token: str
    jti: str
    expires_at: datetime


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    """Verify a plain password against a hashed password."""
    if not plain_password or not hashed_password:
        return False

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """Hash a password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def utc_now() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


def normalize_utc_datetime(value: datetime) -> datetime:
    """Normalize naive datetimes from the DB to UTC-aware values."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def is_expired(value: datetime, now: datetime | None = None) -> bool:
    """Check whether a timestamp has expired."""
    current_time = normalize_utc_datetime(now or utc_now())
    return normalize_utc_datetime(value) <= current_time


def issue_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> AccessTokenContext:
    """Create a JWT access token together with its server-side session metadata."""
    to_encode = data.copy()
    now = utc_now()
    expire = now + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    jti = uuid4().hex
    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "jti": jti,
        }
    )
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return AccessTokenContext(token=encoded_jwt, jti=jti, expires_at=expire)


def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    return issue_access_token(data).token


def decode_access_token(token: str) -> dict:
    """Decode a JWT access token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
