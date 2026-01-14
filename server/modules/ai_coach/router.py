from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from modules.applications.models import Application
from modules.ai_coach.service import generate_feedback 

router = APIRouter(prefix="/ai-coach", tags=["AI Coach"])

@router.post("/analyze/{application_id}")
def analyze_application(application_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    
    if not app:
        return {"error": "Application không tồn tại"}

    feedback = generate_feedback(
        cv_skills=app.cv.skills, 
        job_description=app.job.description
    )
    
    return {
        "application_id": application_id,
        "candidate": app.cv.full_name,
        "job_title": app.job.title,
        "analysis": feedback
    }