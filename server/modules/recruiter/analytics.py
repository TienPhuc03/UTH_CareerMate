#Tính toán các thống kê Dashboard cho nhà tuyển dụng
from sqlalchemy.orm import Session
from sqlalchemy import func
from server.modules.jobs.model import Job
from server.modules.applications.model import Application

def get_recruiter_stats(db: Session, recruiter_id: int):

    total_jobs = db.query(Job).filter(Job.recruiter_id == recruiter_id).count()
    
    total_apps = db.query(Application).join(Job).filter(Job.recruiter_id == recruiter_id).count()
    
    status_counts = db.query(
        Application.status, func.count(Application.id)
    ).join(Job).filter(Job.recruiter_id == recruiter_id).group_by(Application.status).all()
    
    return {
        "total_jobs": total_jobs,
        "total_applications": total_apps,
        "status_distribution": dict(status_counts)
    }