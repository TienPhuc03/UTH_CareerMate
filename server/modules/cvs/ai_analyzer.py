"""
Gemini AI analyzer utilities.
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

from core.config import settings
from core.logging_config import get_logger

try:
    from google import genai
    from google.genai import types
    GENAI_IMPORT_ERROR: Optional[str] = None
except Exception as exc:  # pragma: no cover - depends on runtime env
    genai = None
    types = None
    GENAI_IMPORT_ERROR = str(exc)


logger = get_logger(__name__)

_client = None
_client_init_error: Optional[str] = None


def _initialize_client() -> None:
    """Initialize the Gemini client once and keep failure reasons available."""
    global _client, _client_init_error

    if _client is not None or _client_init_error is not None:
        return

    if GENAI_IMPORT_ERROR:
        _client_init_error = f"google-genai import failed: {GENAI_IMPORT_ERROR}"
        logger.error(_client_init_error)
        return

    if not settings.GEMINI_API_KEY:
        _client_init_error = "GEMINI_API_KEY is not configured"
        logger.error(_client_init_error)
        return

    try:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as exc:  # pragma: no cover - depends on runtime env
        _client_init_error = f"Gemini client init failed: {exc}"
        logger.error(_client_init_error)


def get_gemini_runtime_status() -> Dict[str, Any]:
    """Return the current Gemini runtime health."""
    _initialize_client()
    return {
        "status": "ready" if _client is not None else "unavailable",
        "client_ready": _client is not None,
        "model": settings.GEMINI_MODEL,
        "error": _client_init_error,
    }


def _to_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_analysis_payload(payload: dict[str, Any]) -> Dict[str, Any]:
    return {
        "analysis_status": "success",
        "ats_score": int(payload.get("ats_score") or 0),
        "overall_assessment": payload.get("overall_assessment") or "AI analysis completed.",
        "strengths": _to_string_list(payload.get("strengths")),
        "weaknesses": _to_string_list(payload.get("weaknesses")),
        "improvement_suggestions": _to_string_list(payload.get("improvement_suggestions")),
        "skills_found": _to_string_list(payload.get("skills_found")),
        "error": None,
    }


def _create_fallback_analysis(
    cv_text: str,
    status: str = "fallback",
    error: str | None = None,
) -> Dict[str, Any]:
    """Return a structured fallback payload that the UI can still render."""
    skills = ["python", "java", "javascript", "sql", "react", "docker"]
    found = [skill for skill in skills if skill in (cv_text or "").lower()]
    ats_score = 50 if status == "fallback" else 0

    return {
        "analysis_status": status,
        "ats_score": ats_score,
        "overall_assessment": "AI tam thoi khong kha dung. Dang hien thi ket qua fallback.",
        "strengths": ["CV da tai len thanh cong"],
        "weaknesses": ["Chua the phan tich chi tiet bang AI luc nay"],
        "improvement_suggestions": [
            "Thu phan tich lai sau",
            "Bo sung thanh tich va ky nang cu the",
            "Dam bao CV co noi dung text de he thong doc duoc",
        ],
        "skills_found": found,
        "error": error,
    }


def analyze_cv_with_gemini(
    cv_text: str,
    target_industry: Optional[str] = None,
) -> Dict[str, Any]:
    """Analyze CV using Gemini and always return a renderable payload."""
    _initialize_client()
    start_time = time.time()

    if not _client:
        return _create_fallback_analysis(
            cv_text[:500],
            status="unavailable",
            error=_client_init_error,
        )

    try:
        cv_text_limited = (cv_text or "")[:10000]
        prompt = f"""Ban la chuyen gia HR. Phan tich CV nay.
Nganh: {target_industry or 'IT/Tech'}
CV:
{cv_text_limited}

Output JSON format:
{{
    "ats_score": 0,
    "overall_assessment": "...",
    "strengths": ["..."],
    "weaknesses": ["..."],
    "improvement_suggestions": ["..."],
    "skills_found": ["..."]
}}"""

        response = _client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        payload = json.loads(response.text)
        if not isinstance(payload, dict):
            raise ValueError("Gemini returned a non-object JSON payload")

        result = _normalize_analysis_payload(payload)
        duration = time.time() - start_time
        logger.info(
            "Gemini analysis done. ATS=%s status=%s duration=%.2fs",
            result.get("ats_score"),
            result.get("analysis_status"),
            duration,
        )
        return result
    except Exception as exc:
        logger.error("Gemini analysis error: %s", exc)
        return _create_fallback_analysis(cv_text[:500], status="fallback", error=str(exc))


def generate_career_roadmap(
    cv_skills: str,
    target_role: str,
    current_level: str = "junior",
) -> Dict[str, Any]:
    """Generate career roadmap with Gemini when available."""
    _initialize_client()
    if not _client:
        return {
            "target_role": target_role,
            "estimated_timeline": "6-12 thang",
            "skill_gaps": [],
            "learning_path": [],
            "certifications": [],
            "next_steps": ["Cap nhat CV", "Hoc them ky nang"],
            "tips": "Gemini chua san sang, vui long thu lai sau.",
        }

    try:
        prompt = f"""Tao lo trinh nghe nghiep cho IT tai Viet Nam.

Ky nang hien tai: {cv_skills}
Vi tri muc tieu: {target_role}
Level: {current_level}

Tra ve JSON (khong markdown):
{{
    "target_role": "{target_role}",
    "estimated_timeline": "<thoi gian>",
    "skill_gaps": [
        {{"skill": "<skill>", "priority": "<high/medium/low>", "reason": "<ly do>"}}
    ],
    "learning_path": [
        {{"phase": "1", "duration": "<thoi gian>", "focus": "<trong tam>", "courses": ["<khoa hoc>"], "projects": ["<du an>"]}}
    ],
    "certifications": ["<chung chi 1>"],
    "next_steps": ["<hanh dong 1>", "<hanh dong 2>"],
    "tips": "<loi khuyen>"
}}"""

        response = _client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        text = (response.text or "").strip()
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()

        roadmap = json.loads(text)
        logger.info("Roadmap generated for %s", target_role)
        return roadmap
    except Exception as exc:
        logger.error("Roadmap error: %s", exc)
        return {
            "target_role": target_role,
            "estimated_timeline": "6-12 thang",
            "skill_gaps": [],
            "learning_path": [],
            "certifications": [],
            "next_steps": ["Cap nhat CV", "Hoc them ky nang"],
            "tips": "Hoc tung ky nang mot cach co he thong",
        }


def compare_cv_with_job(cv_text: str, job_description: str) -> Dict[str, Any]:
    """Compare CV with job description using Gemini when available."""
    _initialize_client()
    if not _client:
        return {
            "match_score": 50,
            "matching_skills": [],
            "missing_requirements": [],
            "recommendation": "Gemini chua san sang de so sanh luc nay",
            "cover_letter_tips": [],
        }

    try:
        prompt = f"""So sanh CV voi JD va tra ve JSON (khong markdown).

Job:
{job_description[:1500]}

CV:
{cv_text[:3000]}

JSON:
{{
    "match_score": 0,
    "matching_skills": ["<skill1>"],
    "missing_requirements": ["<thieu 1>"],
    "recommendation": "<nen ung tuyen hay cai thien>",
    "cover_letter_tips": ["<tip1>", "<tip2>"]
}}"""

        response = _client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        text = (response.text or "").strip()
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()

        result = json.loads(text)
        logger.info("CV-Job match: %s", result.get("match_score"))
        return result
    except Exception as exc:
        logger.error("Comparison error: %s", exc)
        return {
            "match_score": 50,
            "matching_skills": [],
            "missing_requirements": [],
            "recommendation": "Khong the phan tich luc nay",
            "cover_letter_tips": [],
        }


_initialize_client()
