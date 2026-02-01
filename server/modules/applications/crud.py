from sqlalchemy.orm import Session
from .models import Application
from .schemas import ApplicationCreate
from modules.jobs.models import Job
from modules.users.models import User

def apply_for_job(db: Session, app_data: ApplicationCreate, user_id: int ):
    new_app = Application(
        job_id=app_data.job_id,
        cv_id=app_data.cv_id,
        user_id=user_id,
        cover_letter=app_data.cover_letter
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

def get_applications_for_recruiter(db: Session, recruiter_id: int):
    results = db.query(
        Application, 
        User.full_name.label("student_name"), 
        User.email.label("student_email"),
        Job.title.label("job_title")
    ).join(User, Application.user_id == User.id)\
     .join(Job, Application.job_id == Job.id)\
     .filter(Job.recruiter_id == recruiter_id).all()
    
    # Chuyển đổi kết quả sang dạng dict để khớp với Schema mới
    output = []
    for app, name, email, title in results:
        app_dict = app.__dict__
        app_dict["student_name"] = name
        app_dict["student_email"] = email
        app_dict["job_title"] = title
        output.append(app_dict)
    return output

def update_status(db: Session, app_id: int, status: str):
    app = db.query(Application).filter(Application.id == app_id).first()
    if app:
        app.status = status
        db.commit()
        db.refresh(app)
    return app