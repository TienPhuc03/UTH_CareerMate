from dataclasses import dataclass

from fastapi import Request

from core.config import settings
from core.logging_config import get_logger
from core.redis_client import RedisClient, redis_client


logger = get_logger(__name__)


@dataclass(frozen=True)
class LoginRateLimitStatus:
    limited: bool
    retry_after: int = 0
    attempts: int = 0


class LoginRateLimiter:
    """Redis-backed rate limiter for password login attempts."""

    def __init__(self, backend: RedisClient = redis_client):
        self.backend = backend
        self._degraded_warning_logged = False

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    def get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for", "").strip()
        if forwarded_for:
            first_ip = forwarded_for.split(",")[0].strip()
            if first_ip:
                return first_ip

        if request.client and request.client.host:
            return request.client.host

        return "unknown"

    def build_key(self, client_ip: str, email: str) -> str:
        normalized_email = self.normalize_email(email)
        return f"auth:login:{client_ip}:{normalized_email}"

    def _warn_degraded(self, message: str) -> None:
        if not self._degraded_warning_logged:
            logger.warning(message)
            self._degraded_warning_logged = True

    def _clear_degraded(self) -> None:
        if self._degraded_warning_logged:
            self._degraded_warning_logged = False

    def is_limited(self, client_ip: str, email: str) -> LoginRateLimitStatus:
        if not settings.LOGIN_RATE_LIMIT_ENABLED:
            return LoginRateLimitStatus(limited=False)

        key = self.build_key(client_ip, email)
        attempts = self.backend.get_int(key)
        if attempts is None:
            self._warn_degraded(
                "Redis unavailable during login rate limit check; allowing login attempts"
            )
            return LoginRateLimitStatus(limited=False)

        self._clear_degraded()

        if attempts < settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS:
            return LoginRateLimitStatus(limited=False, attempts=attempts)

        retry_after = self.backend.ttl(key)
        if retry_after is None:
            self._warn_degraded(
                "Redis unavailable during login rate limit TTL lookup; allowing login attempts"
            )
            return LoginRateLimitStatus(limited=False)

        retry_after = max(retry_after, 1)
        return LoginRateLimitStatus(
            limited=True,
            retry_after=retry_after,
            attempts=attempts,
        )

    def record_failure(self, client_ip: str, email: str) -> LoginRateLimitStatus:
        if not settings.LOGIN_RATE_LIMIT_ENABLED:
            return LoginRateLimitStatus(limited=False)

        key = self.build_key(client_ip, email)
        result = self.backend.increment_counter(
            key=key,
            expire=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
        )
        if result is None:
            self._warn_degraded(
                "Redis unavailable during login rate limit update; allowing login attempts"
            )
            return LoginRateLimitStatus(limited=False)

        self._clear_degraded()
        attempts, retry_after = result

        return LoginRateLimitStatus(
            limited=attempts > settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS,
            retry_after=max(retry_after, 1),
            attempts=attempts,
        )

    def reset(self, client_ip: str, email: str) -> None:
        if not settings.LOGIN_RATE_LIMIT_ENABLED:
            return

        key = self.build_key(client_ip, email)
        deleted = self.backend.delete(key)
        if deleted:
            self._clear_degraded()
            return

        if self.backend.is_connected:
            self._clear_degraded()
        else:
            self._warn_degraded(
                "Redis unavailable during login rate limit reset; continuing without reset"
            )


login_rate_limiter = LoginRateLimiter()
