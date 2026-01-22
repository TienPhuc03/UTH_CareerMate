from sqlalchemy.orm import Session
from sqlalchemy import func
from modules.users.models import User
from modules.jobs.models import Job
from modules.applications.models import Application
from modules.cvs.models import CV

def calculate_user_stats(db: Session):
    return {
        "total": db.query(User).count(),
        "active": db.query(User).filter(User.is_active == True).count(),
        "by_role": {
            "admin": db.query(User).filter(User.role == "admin").count(),
            "candidate": db.query(User).filter(User.role == "candidate").count()
        }
    }

def get_dashboard_stats(db: Session):
    # Tổng hợp tất cả thông số cho Dashboard
    return {
        "users": calculate_user_stats(db),
        "jobs": {"total": db.query(Job).count()},
        "applications": {"total": db.query(Application).count()},
        "cvs": {"total": db.query(CV).count()}
    }