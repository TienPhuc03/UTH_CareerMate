from datetime import datetime, timezone

from modules.users.schemas import Token, UserCreate, UserOut


def test_user_create_accepts_legacy_student_role():
    payload = UserCreate(
        email="legacy@example.com",
        password="secret12",
        full_name="Legacy User",
        role="student",
    )

    assert payload.role == "candidate"


def test_user_out_normalizes_legacy_student_role():
    payload = UserOut.model_validate(
        {
            "id": 1,
            "email": "legacy@example.com",
            "full_name": "Legacy User",
            "role": "student",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
    )

    assert payload.role == "candidate"


def test_token_normalizes_legacy_student_role():
    payload = Token(
        access_token="token",
        token_type="bearer",
        role="student",
        email="legacy@example.com",
    )

    assert payload.role == "candidate"
