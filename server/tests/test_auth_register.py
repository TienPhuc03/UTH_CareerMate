from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from fastapi.testclient import TestClient

import modules.users.router as users_router_module
from core.config import settings
from database.session import SessionLocal
from main import app
from modules.users.models import User


client = TestClient(app)


def _delete_user_by_email(email: str) -> None:
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == email).delete()
        db.commit()
    finally:
        db.close()


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
    finally:
        _delete_user_by_email(email)


def test_google_callback_returns_explicit_google_error():
    response = client.get(
        "/api/Auth/google/callback?error=access_denied",
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Google OAuth error: access_denied"
