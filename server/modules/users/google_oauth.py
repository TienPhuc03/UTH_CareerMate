from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from core.config import settings


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def _require_google_oauth_config() -> None:
    missing_settings = []

    if not settings.GOOGLE_CLIENT_ID:
        missing_settings.append("GOOGLE_CLIENT_ID")
    if not settings.GOOGLE_CLIENT_SECRET:
        missing_settings.append("GOOGLE_CLIENT_SECRET")
    if not settings.GOOGLE_REDIRECT_URI:
        missing_settings.append("GOOGLE_REDIRECT_URI")

    if missing_settings:
        missing_text = ", ".join(missing_settings)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google OAuth is not configured. Missing: {missing_text}",
        )


def _build_google_error_detail(default_message: str, response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        google_error = payload.get("error")
        google_description = payload.get("error_description")
        details = " - ".join(part for part in [google_error, google_description] if part)
        if details:
            return f"{default_message}: {details}"

    response_text = response.text.strip()
    if response_text:
        return f"{default_message}: {response_text}"

    return default_message


def get_google_auth_url() -> str:
    """Create the Google authorization URL."""
    _require_google_oauth_config()

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> dict:
    """Exchange an authorization code for a Google access token."""
    _require_google_oauth_config()

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code from Google")

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=_build_google_error_detail("Failed to exchange Google authorization code", response),
        )

    return response.json()


async def get_google_user_info(access_token: str) -> dict:
    """Fetch the current user's profile from Google."""
    if not access_token:
        raise HTTPException(status_code=400, detail="Missing Google access token")

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=_build_google_error_detail("Failed to fetch Google user info", response),
        )

    return response.json()
