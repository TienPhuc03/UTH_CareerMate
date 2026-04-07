import pathlib
import sys
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import modules.cvs.router as cvs_router_module
from database.session import get_db
from main import app


client = TestClient(app)
TEST_UPLOAD_ROOT = pathlib.Path(__file__).resolve().parent / "_tmp_uploads"


class _FakeQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return None


class _FakeSession:
    def query(self, *_args, **_kwargs):
        return _FakeQuery()


def _override_db():
    yield _FakeSession()


def _make_upload_dir() -> pathlib.Path:
    upload_dir = TEST_UPLOAD_ROOT / uuid4().hex
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def test_upload_cv_returns_cv_id_and_success_analysis(monkeypatch):
    captured = {}
    monkeypatch.setattr(cvs_router_module, "UPLOAD_DIR", str(_make_upload_dir()))
    monkeypatch.setattr(
        cvs_router_module,
        "parse_cv_file",
        lambda *_args, **_kwargs: {
            "raw_text": "Python React SQL",
            "full_name": "Test Candidate",
            "phone": "0123456789",
            "skills": ["python", "react", "sql"],
            "education": "Test University",
        },
    )
    monkeypatch.setattr(
        cvs_router_module,
        "analyze_cv_with_gemini",
        lambda *_args, **_kwargs: {
            "analysis_status": "success",
            "ats_score": 91,
            "overall_assessment": "Strong CV",
            "strengths": ["Clear technical stack"],
            "weaknesses": ["Need more metrics"],
            "improvement_suggestions": ["Add measurable impact"],
            "skills_found": ["python", "react", "sql"],
            "error": None,
        },
    )

    def fake_create_cv(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(id=321)

    monkeypatch.setattr(cvs_router_module, "create_cv", fake_create_cv)
    monkeypatch.setattr(cvs_router_module.redis_client, "set", lambda *_args, **_kwargs: None)
    app.dependency_overrides[get_db] = _override_db

    try:
        response = client.post(
            "/api/cvs/up",
            data={"email": "upload-success@example.com", "target_industry": "Cong nghe thong tin"},
            files={"file": ("sample.pdf", b"%PDF-1.4 sample", "application/pdf")},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["cv_id"] == 321
        assert payload["analysis_status"] == "success"
        assert payload["analysis_error"] is None
        assert payload["ai_analysis"]["ats_score"] == 91
        assert captured["ai_feedback"]["analysis_status"] == "success"
        assert captured["ats_score"] == 91
        assert captured["cv_data"].email == "upload-success@example.com"
    finally:
        app.dependency_overrides.clear()


def test_upload_cv_returns_fallback_response_when_ai_unavailable(monkeypatch):
    captured = {}
    monkeypatch.setattr(cvs_router_module, "UPLOAD_DIR", str(_make_upload_dir()))
    monkeypatch.setattr(
        cvs_router_module,
        "parse_cv_file",
        lambda *_args, **_kwargs: {
            "raw_text": "Designer CV",
            "full_name": "Fallback Candidate",
            "phone": None,
            "skills": [],
            "education": "",
        },
    )
    monkeypatch.setattr(
        cvs_router_module,
        "analyze_cv_with_gemini",
        lambda *_args, **_kwargs: {
            "analysis_status": "unavailable",
            "ats_score": 0,
            "overall_assessment": "AI unavailable",
            "strengths": ["CV saved successfully"],
            "weaknesses": ["AI could not analyze right now"],
            "improvement_suggestions": ["Try again later"],
            "skills_found": [],
            "error": "Gemini unavailable",
        },
    )

    def fake_create_cv(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(id=654)

    monkeypatch.setattr(cvs_router_module, "create_cv", fake_create_cv)
    monkeypatch.setattr(cvs_router_module.redis_client, "set", lambda *_args, **_kwargs: None)
    app.dependency_overrides[get_db] = _override_db

    try:
        response = client.post(
            "/api/cvs/up",
            data={"email": "upload-fallback@example.com"},
            files={"file": ("sample.pdf", b"%PDF-1.4 sample", "application/pdf")},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["cv_id"] == 654
        assert payload["analysis_status"] == "unavailable"
        assert payload["analysis_error"] == "Gemini unavailable"
        assert payload["ai_analysis"]["analysis_status"] == "unavailable"
        assert captured["ai_feedback"]["error"] == "Gemini unavailable"
    finally:
        app.dependency_overrides.clear()


def test_upload_cv_rejects_invalid_file_type(monkeypatch):
    app.dependency_overrides[get_db] = _override_db

    try:
        response = client.post(
            "/api/cvs/up",
            data={"email": "upload-invalid@example.com"},
            files={"file": ("sample.txt", b"plain text", "text/plain")},
        )

        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_upload_cv_returns_422_when_parser_fails(monkeypatch):
    monkeypatch.setattr(cvs_router_module, "UPLOAD_DIR", str(_make_upload_dir()))
    monkeypatch.setattr(
        cvs_router_module,
        "parse_cv_file",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("Cannot read CV")),
    )
    app.dependency_overrides[get_db] = _override_db

    try:
        response = client.post(
            "/api/cvs/up",
            data={"email": "upload-parse-error@example.com"},
            files={"file": ("sample.pdf", b"%PDF-1.4 sample", "application/pdf")},
        )

        assert response.status_code == 422
        assert "Cannot parse CV" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
