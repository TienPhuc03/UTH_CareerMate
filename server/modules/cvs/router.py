

import os
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from core.logging_config import get_logger
from core.redis_client import get_cv_cache_key, redis_client
from database.session import get_db
from core.dependencies import get_current_user
from modules.cvs.ai_analyzer import (
    analyze_cv_with_gemini,
    compare_cv_with_job,
    generate_career_roadmap,
)
from modules.cvs.models import CV
from modules.cvs.parser import parse_cv_file
from modules.cvs.schemas import CVCreate, CVResponse, CVUploadResponse
from modules.cvs.service import create_cv
from modules.users.models import User


router = APIRouter()
logger = get_logger(__name__)

UPLOAD_DIR = "uploads/cvs"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}

os.makedirs(UPLOAD_DIR, exist_ok=True)


def _build_default_ai_analysis(error: str | None = None) -> dict:
    return {
        "analysis_status": "unavailable",
        "ats_score": 0,
        "overall_assessment": "AI tam thoi khong kha dung.",
        "strengths": ["CV da tai len thanh cong"],
        "weaknesses": ["Khong the phan tich chi tiet bang AI luc nay"],
        "improvement_suggestions": ["Thu lai sau khi he thong AI san sang"],
        "skills_found": [],
        "error": error or "Analyzer did not return a valid payload",
    }


def can_access_cv(current_user: User, cv: CV) -> bool:
    """Admin can access all CVs; candidate can access only their own CV."""
    if current_user.role == "admin":
        return True

    if current_user.role == "candidate" and cv.user_id == current_user.id:
        return True

    return False


def can_delete_cv(current_user: User, cv: CV) -> bool:
    """Admin can delete all CVs; candidate can delete only their own CV."""
    if current_user.role == "admin":
        return True

    if current_user.role == "candidate" and cv.user_id == current_user.id:
        return True

    return False


@router.post("/up", response_model=CVUploadResponse)
def upload_cv_file(
    file: UploadFile = File(...),
    target_industry: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a CV, analyze it, and return data needed by the result page."""
    email = current_user.email
    user_id = current_user.id

    logger.info("CV upload started: %s", email)

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File qua lon. Vui long tai file duoi 5MB."
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chi chap nhan file PDF, DOC hoac DOCX."
        )

    if not file.filename or "." not in file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ten file khong hop le."
        )

    file_ext = file.filename.rsplit(".", 1)[-1].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{email.split('@')[0]}_{timestamp}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info("File saved: %s", filename)

    try:
        parsed_data = parse_cv_file(file_path, file_ext)
        logger.info("CV parsed. Found %s skills", len(parsed_data.get("skills", [])))
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error("Parse failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot parse CV: {exc}"
        ) from exc

    ai_analysis = None
    unexpected_ai_error = None
    try:
        ai_analysis = analyze_cv_with_gemini(
            cv_text=parsed_data.get("raw_text", ""),
            target_industry=target_industry,
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("AI analysis failed unexpectedly: %s", exc)
        unexpected_ai_error = str(exc)

    if not isinstance(ai_analysis, dict):
        ai_analysis = _build_default_ai_analysis(unexpected_ai_error)

    analysis_status = ai_analysis.get("analysis_status", "success")
    analysis_error = ai_analysis.get("error")

    cv_data = CVCreate(
        full_name=parsed_data.get("full_name", "Unknown"),
        email=email,
        phone=parsed_data.get("phone"),
        skills=", ".join(parsed_data.get("skills", [])),
        experience=parsed_data.get("raw_text", "")[:2000],
        education=parsed_data.get("education", ""),
    )

    cv_record = create_cv(
        db=db,
        cv_data=cv_data,
        user_id=user_id,
        file_path=file_path,
        file_name=filename,
        file_type=file_ext,
        ats_score=ai_analysis.get("ats_score"),
        ai_feedback=ai_analysis,
    )

    logger.info("CV saved to DB: ID=%s", cv_record.id)
    redis_client.set(get_cv_cache_key(cv_record.id), ai_analysis, expire=3600)

    return {
        "cv_id": cv_record.id,
        "message": "CV uploaded successfully",
        "analysis_status": analysis_status,
        "analysis_error": analysis_error,
        "parsed_data": {
            "full_name": parsed_data.get("full_name"),
            "email": email,
            "skills_count": len(parsed_data.get("skills", [])),
        },
        "ats_score": ai_analysis.get("ats_score"),
        "ai_analysis": ai_analysis,
        "file_info": {
            "filename": filename,
            "size_kb": round(file_size / 1024, 2),
        },
    }


@router.get("/", response_model=List[CVResponse])
def list_cvs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all CVs. Only admin can view all CVs."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can view all CVs"
        )

    return db.query(CV).offset(skip).limit(limit).all()


@router.get("/{cv_id}", response_model=CVResponse)
def get_cv_by_id(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a CV by ID with ownership check."""
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )

    if not can_access_cv(current_user, cv):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this CV"
        )

    return cv


@router.post("/analyze/{cv_id}")
def re_analyze_cv(
    cv_id: int,
    target_industry: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Re-run AI analysis for an existing CV."""
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )

    if not can_access_cv(current_user, cv):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to analyze this CV"
        )

    cache_key = get_cv_cache_key(cv_id)
    cached = redis_client.get(cache_key)

    if cached:
        logger.info("Cache HIT for CV %s", cv_id)
        return {
            "cv_id": cv_id,
            "analysis": cached,
            "analysis_status": cached.get("analysis_status", "success"),
            "analysis_error": cached.get("error"),
            "from_cache": True,
        }

    logger.info("Cache MISS for CV %s, analyzing...", cv_id)
    analysis = analyze_cv_with_gemini(cv.experience or "", target_industry)

    redis_client.set(cache_key, analysis, expire=3600)
    cv.ai_feedback = analysis
    cv.ats_score = analysis.get("ats_score")
    db.commit()

    return {
        "cv_id": cv_id,
        "analysis": analysis,
        "analysis_status": analysis.get("analysis_status", "success"),
        "analysis_error": analysis.get("error"),
        "from_cache": False,
    }


@router.post("/roadmap/{cv_id}")
def get_career_roadmap(
    cv_id: int,
    target_role: str = Query(...),
    current_level: str = Query("junior"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a career roadmap for the uploaded CV."""
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )

    if not can_access_cv(current_user, cv):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this CV roadmap"
        )

    roadmap = generate_career_roadmap(
        cv_skills=cv.skills or "",
        target_role=target_role,
        current_level=current_level,
    )

    return {
        "cv_id": cv_id,
        "candidate": cv.full_name,
        "roadmap": roadmap,
    }


@router.post("/compare/{cv_id}/job/{job_id}")
def compare_cv_job(
    cv_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare a CV with a job description."""
    from modules.jobs.models import Job

    cv = db.query(CV).filter(CV.id == cv_id).first()
    job = db.query(Job).filter(Job.id == job_id).first()

    if not cv or not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV or Job not found"
        )

    if not can_access_cv(current_user, cv):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to compare this CV"
        )

    comparison = compare_cv_with_job(
        cv_text=cv.experience or "",
        job_description=job.description or "",
    )

    return {
        "cv_id": cv_id,
        "job_id": job_id,
        "candidate": cv.full_name,
        "job_title": job.title,
        "comparison": comparison,
    }


@router.delete("/{cv_id}")
def delete_cv(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a CV and clear cached analysis."""
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )

    if not can_delete_cv(current_user, cv):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this CV"
        )

    if cv.file_path and os.path.exists(cv.file_path):
        try:
            os.remove(cv.file_path)
            logger.info("Deleted file: %s", cv.file_path)
        except Exception as exc:
            logger.error("Error deleting file: %s", exc)

    db.delete(cv)
    db.commit()
    redis_client.delete(get_cv_cache_key(cv_id))

    logger.info("CV %s deleted", cv_id)
    return {"message": "CV deleted successfully"}