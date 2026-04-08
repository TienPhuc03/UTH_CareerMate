from datetime import timedelta
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from fastapi.testclient import TestClient

import modules.users.router as users_router_module
from core.auth_rate_limit import LoginRateLimiter
from core import security
from core.config import settings
from database.session import SessionLocal
from main import app
from modules.users.models import User, UserSession


client = TestClient(app)


class _FakeRateLimitRedis:
    def __init__(self):
        self.is_connected = True
        self._store: dict[str, dict[str, int]] = {}
        self.now = 0

    def _purge_if_expired(self, key: str) -> None:
        entry = self._store.get(key)
        if entry and entry["expires_at"] <= self.now:
            self._store.pop(key, None)

    def get_int(self, key: str) -> int | None:
        self._purge_if_expired(key)
        entry = self._store.get(key)
        if entry is None:
            return 0
        return entry["count"]

    def ttl(self, key: str) -> int | None:
        self._purge_if_expired(key)
        entry = self._store.get(key)
        if entry is None:
            return 0
        return max(entry["expires_at"] - self.now, 0)

    def increment_counter(self, key: str, expire: int) -> tuple[int, int] | None:
        self._purge_if_expired(key)
        entry = self._store.get(key)
        if entry is None:
            entry = {"count": 0, "expires_at": self.now + expire}
            self._store[key] = entry
        entry["count"] += 1
        return entry["count"], max(entry["expires_at"] - self.now, 1)

    def delete(self, key: str) -> bool:
        self._purge_if_expired(key)
        return self._store.pop(key, None) is not None

    def advance(self, seconds: int) -> None:
        self.now += seconds


class _UnavailableRateLimitRedis:
    is_connected = False

    def get_int(self, key: str) -> int | None:
        return None

    def ttl(self, key: str) -> int | None:
        return None

    def increment_counter(self, key: str, expire: int) -> tuple[int, int] | None:
        return None

    def delete(self, key: str) -> bool:
        return False


def _delete_user_by_email(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.query(UserSession).filter(UserSession.user_id == user.id).delete()
            db.delete(user)
            db.commit()
    finally:
        db.close()


def _get_user_role_by_email(email: str) -> str | None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user.role if user else None
    finally:
        db.close()


def _get_session_by_jti(jti: str) -> UserSession | None:
    db = SessionLocal()
    try:
        return db.query(UserSession).filter(UserSession.token == jti).first()
    finally:
        db.close()


def _delete_session_by_jti(jti: str) -> None:
    db = SessionLocal()
    try:
        db.query(UserSession).filter(UserSession.token == jti).delete()
        db.commit()
    finally:
        db.close()


def _expire_session_by_jti(jti: str) -> None:
    db = SessionLocal()
    try:
        session = db.query(UserSession).filter(UserSession.token == jti).first()
        if session:
            session.expires_at = security.utc_now() - timedelta(minutes=1)
            db.commit()
    finally:
        db.close()


def _register_user(email: str, password: str = "secret12") -> None:
    response = client.post(
        "/api/Auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Rate Limit User",
            "role": "candidate",
        },
    )
    assert response.status_code == 201


def test_register_returns_201_for_valid_payload():
    email = f"register-{uuid4().hex[:8]}@example.com"

    try:
        response = client.post(
            "/api/Auth/register",
            json={
                "email": email,
                "password": "secret12",
                "full_name": "Test Register",
                "role": "candidate",
            },
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["email"] == email
        assert payload["full_name"] == "Test Register"
        assert payload["role"] == "candidate"
    finally:
        _delete_user_by_email(email)


def test_register_returns_422_when_full_name_missing():
    response = client.post(
        "/api/Auth/register",
        json={
            "email": f"missing-{uuid4().hex[:8]}@example.com",
            "password": "secret12",
            "role": "candidate",
        },
    )

    assert response.status_code == 422


def test_register_rejects_public_admin_role():
    response = client.post(
        "/api/Auth/register",
        json={
            "email": f"admin-{uuid4().hex[:8]}@example.com",
            "password": "secret12",
            "full_name": "Admin Candidate",
            "role": "admin",
        },
    )

    assert response.status_code == 403


def test_register_accepts_legacy_student_role_alias():
    email = f"student-{uuid4().hex[:8]}@example.com"

    try:
        response = client.post(
            "/api/Auth/register",
            json={
                "email": email,
                "password": "secret12",
                "full_name": "Student Alias",
                "role": "student",
            },
        )

        assert response.status_code == 201
        assert response.json()["role"] == "candidate"
    finally:
        _delete_user_by_email(email)


def test_login_creates_server_session():
    email = f"login-{uuid4().hex[:8]}@example.com"

    try:
        _register_user(email)

        response = client.post(
            "/api/Auth/login",
            json={
                "email": email,
                "password": "secret12",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        token_payload = security.decode_access_token(payload["access_token"])

        assert token_payload["sub"] == email
        assert token_payload["jti"]

        user_session = _get_session_by_jti(token_payload["jti"])
        assert user_session is not None
        assert user_session.expires_at is not None
    finally:
        _delete_user_by_email(email)


def test_login_rate_limit_blocks_sixth_failed_attempt(monkeypatch):
    email = f"rate-limit-{uuid4().hex[:8]}@example.com"
    headers = {"X-Forwarded-For": "203.0.113.10"}
    fake_redis = _FakeRateLimitRedis()

    monkeypatch.setattr(
        users_router_module,
        "login_rate_limiter",
        LoginRateLimiter(fake_redis),
    )

    try:
        _register_user(email)

        for _ in range(5):
            response = client.post(
                "/api/Auth/login",
                json={"email": email, "password": "wrongpass"},
                headers=headers,
            )
            assert response.status_code == 401

        blocked_response = client.post(
            "/api/Auth/login",
            json={"email": email, "password": "wrongpass"},
            headers=headers,
        )

        assert blocked_response.status_code == 429
        assert "Qua nhieu lan dang nhap" in blocked_response.json()["detail"]
        assert blocked_response.headers["Retry-After"] == "900"
    finally:
        _delete_user_by_email(email)


def test_login_rate_limit_resets_after_successful_login(monkeypatch):
    email = f"rate-reset-{uuid4().hex[:8]}@example.com"
    headers = {"X-Forwarded-For": "203.0.113.11"}
    fake_redis = _FakeRateLimitRedis()

    monkeypatch.setattr(
        users_router_module,
        "login_rate_limiter",
        LoginRateLimiter(fake_redis),
    )

    try:
        _register_user(email)

        for _ in range(4):
            response = client.post(
                "/api/Auth/login",
                json={"email": email, "password": "wrongpass"},
                headers=headers,
            )
            assert response.status_code == 401

        successful_response = client.post(
            "/api/Auth/login",
            json={"email": email, "password": "secret12"},
            headers=headers,
        )
        assert successful_response.status_code == 200

        next_failure_response = client.post(
            "/api/Auth/login",
            json={"email": email, "password": "wrongpass"},
            headers=headers,
        )
        assert next_failure_response.status_code == 401
    finally:
        _delete_user_by_email(email)


def test_login_rate_limit_retry_after_decreases_with_ttl(monkeypatch):
    email = f"rate-ttl-{uuid4().hex[:8]}@example.com"
    headers = {"X-Forwarded-For": "203.0.113.12"}
    fake_redis = _FakeRateLimitRedis()

    monkeypatch.setattr(
        users_router_module,
        "login_rate_limiter",
        LoginRateLimiter(fake_redis),
    )

    try:
        _register_user(email)

        for _ in range(5):
            response = client.post(
                "/api/Auth/login",
                json={"email": email, "password": "wrongpass"},
                headers=headers,
            )
            assert response.status_code == 401

        first_blocked_response = client.post(
            "/api/Auth/login",
            json={"email": email, "password": "wrongpass"},
            headers=headers,
        )
        assert first_blocked_response.status_code == 429
        first_retry_after = int(first_blocked_response.headers["Retry-After"])

        fake_redis.advance(10)

        second_blocked_response = client.post(
            "/api/Auth/login",
            json={"email": email, "password": "wrongpass"},
            headers=headers,
        )
        assert second_blocked_response.status_code == 429
        second_retry_after = int(second_blocked_response.headers["Retry-After"])

        assert second_retry_after < first_retry_after
    finally:
        _delete_user_by_email(email)


def test_login_rate_limit_keys_are_separated_by_ip_and_email(monkeypatch):
    email = f"rate-key-{uuid4().hex[:8]}@example.com"
    second_email = f"rate-key-alt-{uuid4().hex[:8]}@example.com"
    primary_headers = {"X-Forwarded-For": "203.0.113.13"}
    alternate_ip_headers = {"X-Forwarded-For": "203.0.113.14"}
    fake_redis = _FakeRateLimitRedis()

    monkeypatch.setattr(
        users_router_module,
        "login_rate_limiter",
        LoginRateLimiter(fake_redis),
    )

    try:
        _register_user(email)
        _register_user(second_email)

        for _ in range(5):
            response = client.post(
                "/api/Auth/login",
                json={"email": email, "password": "wrongpass"},
                headers=primary_headers,
            )
            assert response.status_code == 401

        same_ip_other_email = client.post(
            "/api/Auth/login",
            json={"email": second_email, "password": "wrongpass"},
            headers=primary_headers,
        )
        assert same_ip_other_email.status_code == 401

        same_email_other_ip = client.post(
            "/api/Auth/login",
            json={"email": email, "password": "wrongpass"},
            headers=alternate_ip_headers,
        )
        assert same_email_other_ip.status_code == 401
    finally:
        _delete_user_by_email(email)
        _delete_user_by_email(second_email)


def test_login_rate_limit_fails_open_when_redis_is_unavailable(monkeypatch):
    email = f"rate-open-{uuid4().hex[:8]}@example.com"
    headers = {"X-Forwarded-For": "203.0.113.15"}

    monkeypatch.setattr(
        users_router_module,
        "login_rate_limiter",
        LoginRateLimiter(_UnavailableRateLimitRedis()),
    )

    try:
        _register_user(email)

        for _ in range(6):
            response = client.post(
                "/api/Auth/login",
                json={"email": email, "password": "wrongpass"},
                headers=headers,
            )
            assert response.status_code == 401

        success_response = client.post(
            "/api/Auth/login",
            json={"email": email, "password": "secret12"},
            headers=headers,
        )
        assert success_response.status_code == 200
    finally:
        _delete_user_by_email(email)


def test_logout_revokes_current_token():
    email = f"logout-{uuid4().hex[:8]}@example.com"

    try:
        register_response = client.post(
            "/api/Auth/register",
            json={
                "email": email,
                "password": "secret12",
                "full_name": "Logout Session",
                "role": "candidate",
            },
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/api/Auth/login",
            json={
                "email": email,
                "password": "secret12",
            },
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        token_payload = security.decode_access_token(token)
        headers = {"Authorization": f"Bearer {token}"}

        profile_response = client.get("/api/Auth/profile", headers=headers)
        assert profile_response.status_code == 200

        logout_response = client.post("/api/Auth/logout", headers=headers)
        assert logout_response.status_code == 200
        assert logout_response.json()["message"] == "Dang xuat thanh cong"
        assert _get_session_by_jti(token_payload["jti"]) is None

        revoked_response = client.get("/api/Auth/profile", headers=headers)
        assert revoked_response.status_code == 401
    finally:
        _delete_user_by_email(email)


def test_profile_rejects_token_without_active_session():
    email = f"missing-session-{uuid4().hex[:8]}@example.com"

    try:
        register_response = client.post(
            "/api/Auth/register",
            json={
                "email": email,
                "password": "secret12",
                "full_name": "Missing Session",
                "role": "candidate",
            },
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/api/Auth/login",
            json={
                "email": email,
                "password": "secret12",
            },
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        token_payload = security.decode_access_token(token)
        _delete_session_by_jti(token_payload["jti"])

        response = client.get(
            "/api/Auth/profile",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
    finally:
        _delete_user_by_email(email)


def test_profile_rejects_token_with_expired_session():
    email = f"expired-session-{uuid4().hex[:8]}@example.com"

    try:
        register_response = client.post(
            "/api/Auth/register",
            json={
                "email": email,
                "password": "secret12",
                "full_name": "Expired Session",
                "role": "candidate",
            },
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/api/Auth/login",
            json={
                "email": email,
                "password": "secret12",
            },
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        token_payload = security.decode_access_token(token)
        _expire_session_by_jti(token_payload["jti"])

        response = client.get(
            "/api/Auth/profile",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        assert _get_session_by_jti(token_payload["jti"]) is None
    finally:
        _delete_user_by_email(email)


def test_google_callback_creates_user_without_crashing(monkeypatch):
    email = f"google-{uuid4().hex[:8]}@example.com"

    async def fake_exchange_code_for_token(code: str) -> dict:
        assert code == "fake-code"
        return {"access_token": "google-access-token"}

    async def fake_get_google_user_info(access_token: str) -> dict:
        assert access_token == "google-access-token"
        return {"email": email, "name": "Google User"}

    monkeypatch.setattr(users_router_module, "exchange_code_for_token", fake_exchange_code_for_token)
    monkeypatch.setattr(users_router_module, "get_google_user_info", fake_get_google_user_info)

    try:
        response = client.get("/api/Auth/google/callback?code=fake-code", follow_redirects=False)
        redirect_url = urlparse(response.headers["location"])
        query = parse_qs(redirect_url.query)

        assert response.status_code in {302, 307}
        assert response.headers["location"].startswith(settings.GOOGLE_OAUTH_SUCCESS_REDIRECT_URL)
        assert query["email"] == [email]
        assert query["role"] == ["candidate"]
        assert query["token"]
        token_payload = security.decode_access_token(query["token"][0])
        assert _get_session_by_jti(token_payload["jti"]) is not None
    finally:
        _delete_user_by_email(email)


def test_google_login_includes_state_with_selected_recruiter_role(monkeypatch):
    captured: dict[str, str | None] = {"state": None}

    def fake_get_google_auth_url(state: str | None = None) -> str:
        captured["state"] = state
        return "https://example.com/google-oauth"

    monkeypatch.setattr(users_router_module, "get_google_auth_url", fake_get_google_auth_url)
    response = client.get("/api/Auth/google/login?role=recruiter", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "https://example.com/google-oauth"
    oauth_state = captured["state"]

    assert oauth_state
    decoded_role = users_router_module.decode_google_oauth_state(oauth_state)
    assert decoded_role == "recruiter"


def test_google_callback_creates_new_user_with_recruiter_role_from_state(monkeypatch):
    email = f"google-recruiter-{uuid4().hex[:8]}@example.com"
    oauth_state = users_router_module.encode_google_oauth_state("recruiter")

    async def fake_exchange_code_for_token(code: str) -> dict:
        assert code == "fake-code"
        return {"access_token": "google-access-token"}

    async def fake_get_google_user_info(access_token: str) -> dict:
        assert access_token == "google-access-token"
        return {"email": email, "name": "Google Recruiter"}

    monkeypatch.setattr(users_router_module, "exchange_code_for_token", fake_exchange_code_for_token)
    monkeypatch.setattr(users_router_module, "get_google_user_info", fake_get_google_user_info)

    try:
        response = client.get(
            f"/api/Auth/google/callback?code=fake-code&state={oauth_state}",
            follow_redirects=False,
        )
        redirect_url = urlparse(response.headers["location"])
        query = parse_qs(redirect_url.query)

        assert response.status_code in {302, 307}
        assert query["email"] == [email]
        assert query["role"] == ["recruiter"]
        assert _get_user_role_by_email(email) == "recruiter"
    finally:
        _delete_user_by_email(email)


def test_google_callback_keeps_existing_user_role_even_if_state_is_recruiter(monkeypatch):
    email = f"google-existing-{uuid4().hex[:8]}@example.com"
    oauth_state = users_router_module.encode_google_oauth_state("recruiter")

    db = SessionLocal()
    try:
        db.add(
            User(
                email=email,
                full_name="Existing Candidate",
                hashed_password=None,
                role="candidate",
                is_active=True,
            )
        )
        db.commit()
    finally:
        db.close()

    async def fake_exchange_code_for_token(code: str) -> dict:
        assert code == "fake-code"
        return {"access_token": "google-access-token"}

    async def fake_get_google_user_info(access_token: str) -> dict:
        assert access_token == "google-access-token"
        return {"email": email, "name": "Existing Candidate"}

    monkeypatch.setattr(users_router_module, "exchange_code_for_token", fake_exchange_code_for_token)
    monkeypatch.setattr(users_router_module, "get_google_user_info", fake_get_google_user_info)

    try:
        response = client.get(
            f"/api/Auth/google/callback?code=fake-code&state={oauth_state}",
            follow_redirects=False,
        )
        redirect_url = urlparse(response.headers["location"])
        query = parse_qs(redirect_url.query)

        assert response.status_code in {302, 307}
        assert query["email"] == [email]
        assert query["role"] == ["candidate"]
        assert _get_user_role_by_email(email) == "candidate"
    finally:
        _delete_user_by_email(email)


def test_google_callback_returns_explicit_google_error():
    response = client.get(
        "/api/Auth/google/callback?error=access_denied",
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Google OAuth error: access_denied"
