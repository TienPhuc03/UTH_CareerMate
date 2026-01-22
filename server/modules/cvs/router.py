
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from database.session import get_db
from modules.cvs.schemas import CVCreate, CVResponse
from modules.cvs.service import create_cv, get_all_cvs
from modules.cvs.parser import parse_cv_file
from modules.cvs.ai_analyzer import (
    analyze_cv_with_gemini,
    generate_career_roadmap,
    compare_cv_with_job
)
from modules.cvs.models import CV
from core.logging_config import get_logger
from core.redis_client import redis_client, get_cv_cache_key, get_job_recommendations_key



router = APIRouter()
logger = get_logger(__name__)

UPLOAD_DIR = "uploads/cvs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload_cv_file(
    file: UploadFile = File(...),
    email: str = Form(...),
    target_industry: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and analyze CV with Gemini AI"""
    logger.info(f"📤 CV upload started: {email}")
    
    # Validate file
    if file.content_type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        raise HTTPException(400, "Only PDF and DOCX allowed")
    
    # Save file
    file_ext = file.filename.split('.')[-1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{email.split('@')[0]}_{timestamp}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logger.info(f"💾 File saved: {filename}")
    
    # Parse CV
    try:
        parsed_data = parse_cv_file(file_path, file_ext)
        logger.info(f"✅ CV parsed. Found {len(parsed_data['skills'])} skills")
    except Exception as e:
        os.remove(file_path)
        logger.error(f"❌ Parse failed: {e}")
        raise HTTPException(422, f"Cannot parse CV: {e}")
    
    # Analyze with Gemini
    ai_analysis = None
    try:
        ai_analysis = analyze_cv_with_gemini(
            cv_text=parsed_data['raw_text'],
            target_industry=target_industry
        )
    except Exception as e:
        logger.warning(f"⚠️  AI analysis failed: {e}")
    
    # Save to DB
    cv_data = CVCreate(
        full_name=parsed_data.get('full_name', 'Unknown'),
        email=email,
        phone=parsed_data.get('phone'),
        skills=', '.join(parsed_data.get('skills', [])),
        experience=parsed_data.get('raw_text', '')[:2000]
    )
    
    cv_record = create_cv(db, cv_data)
    logger.info(f"✅ CV saved to DB: ID={cv_record.id}")
    
    # Cache AI analysis
    if ai_analysis:
        cache_key = get_cv_cache_key(cv_record.id)
        redis_client.set(cache_key, ai_analysis, expire=3600)
    
    return {
        "cv_id": cv_record.id,
        "message": "CV uploaded successfully",
        "parsed_data": {
            "full_name": parsed_data.get('full_name'),
            "email": email,
            "phone": parsed_data.get('phone'),
            "skills": parsed_data.get('skills'),
            "skills_count": len(parsed_data.get('skills', []))
        },
        "ai_analysis": ai_analysis,
        "file_info": {
            "filename": filename,
            "size_kb": round(os.path.getsize(file_path) / 1024, 2)
        }
    }


@router.get("/", response_model=List[CVResponse])
def list_cvs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all CVs"""
    cvs = db.query(CV).offset(skip).limit(limit).all()
    return cvs


@router.get("/{cv_id}", response_model=CVResponse)
def get_cv_by_id(cv_id: int, db: Session = Depends(get_db)):
    """Get CV by ID"""
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(404, "CV not found")
    return cv


@router.post("/analyze/{cv_id}")
def re_analyze_cv(
    cv_id: int,
    target_industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Re-analyze CV with caching"""
    
    # Check cache first
    cache_key = get_cv_cache_key(cv_id)
    cached = redis_client.get(cache_key)
    
    if cached:
        logger.info(f"🎯 Cache HIT for CV {cv_id}")
        return {
            "cv_id": cv_id,
            "analysis": cached,
            "from_cache": True
        }
    
    # Cache miss - analyze
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(404, "CV not found")
    
    logger.info(f"🔄 Cache MISS for CV {cv_id}, analyzing...")
    analysis = analyze_cv_with_gemini(cv.experience, target_industry)
    
    # Cache result
    redis_client.set(cache_key, analysis, expire=3600)
    
    return {
        "cv_id": cv_id,
        "analysis": analysis,
        "from_cache": False
    }


@router.post("/roadmap/{cv_id}")
def get_career_roadmap(
    cv_id: int,
    target_role: str = Query(...),
    current_level: str = Query("junior"),
    db: Session = Depends(get_db)
):
    """Generate career roadmap"""
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(404, "CV not found")
    
    roadmap = generate_career_roadmap(
        cv_skills=cv.skills or "",
        target_role=target_role,
        current_level=current_level
    )
    
    return {
        "cv_id": cv_id,
        "candidate": cv.full_name,
        "roadmap": roadmap
    }


@router.post("/compare/{cv_id}/job/{job_id}")
def compare_cv_job(
    cv_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    """Compare CV with job"""
    from modules.jobs.models import Job
    
    cv = db.query(CV).filter(CV.id == cv_id).first()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not cv or not job:
        raise HTTPException(404, "CV or Job not found")
    
    comparison = compare_cv_with_job(
        cv_text=cv.experience or "",
        job_description=job.description or ""
    )
    
    return {
        "cv_id": cv_id,
        "job_id": job_id,
        "candidate": cv.full_name,
        "job_title": job.title,
        "comparison": comparison
    }


@router.delete("/{cv_id}")
def delete_cv(cv_id: int, db: Session = Depends(get_db)):
    """Delete CV and clear cache"""
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(404, "CV not found")
    
    # Delete from DB
    db.delete(cv)
    db.commit()
    
    # Clear cache
    cache_key = get_cv_cache_key(cv_id)
    redis_client.delete(cache_key)
    
    logger.info(f"🗑️  CV {cv_id} deleted")
    
    return {"message": "CV deleted successfully"}