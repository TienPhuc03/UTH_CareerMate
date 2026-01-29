from sqlalchemy.orm import Session
from modules.users.models import User
from modules.jobs.models import Job
from modules.applications.models import Application

def get_dashboard_stats(db: Session):
    """Tổng hợp số liệu thống kê cho Admin Dashboard"""
    
    # 1. Thống kê User
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # 2. Thống kê Job
    total_jobs = db.query(Job).count()
    active_jobs = db.query(Job).filter(Job.status == "active").count()
    
    # 3. Thống kê Applications
    total_applications = db.query(Application).count()

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "jobs": {
            "total": total_jobs,
            "active": active_jobs,
            "closed": total_jobs - active_jobs
        },
        "applications": {
            "total": total_applications
        }
    }