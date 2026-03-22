from datetime import datetime

from sqlalchemy.orm import Session

from modules.applications.models import Application
from modules.applications.schemas import ApplicationCreate
from modules.jobs.models import Job
from modules.users.models import User


def apply_for_job(db: Session, app_data: ApplicationCreate, user_id: int):
    new_app = Application(
        job_id=app_data.job_id,
        cv_id=app_data.cv_id,
        user_id=user_id,
        cover_letter=app_data.cover_letter,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app


def get_applications_for_recruiter(db: Session, recruiter_id: int):
    results = (
        db.query(
            Application,
            User.full_name.label("student_name"),
            User.email.label("student_email"),
            Job.title.label("job_title"),
        )
        .join(User, Application.user_id == User.id)
        .join(Job, Application.job_id == Job.id)
        .filter(Job.recruiter_id == recruiter_id)
        .order_by(Application.created_at.desc())
        .all()
    )

    output = []
    for app, name, email, title in results:
        output.append(
            {
                "id": app.id,
                "job_id": app.job_id,
                "cv_id": app.cv_id,
                "user_id": app.user_id,
                "status": app.status,
                "created_at": app.created_at,
                "student_name": name,
                "student_email": email,
                "job_title": title,
            }
        )
    return output


def update_status(db: Session, app_id: int, recruiter_id: int, status: str):
    app = (
        db.query(Application)
        .join(Job, Application.job_id == Job.id)
        .filter(Application.id == app_id, Job.recruiter_id == recruiter_id)
        .first()
    )
    if app:
        app.status = status
        if status != "PENDING":
            app.reviewed_at = datetime.utcnow()
        db.commit()
        db.refresh(app)
    return app
