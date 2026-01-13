import sys
import os
from fastapi import FastAPI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.modules.jobs.router import router as jobs_router 
from server.modules.cvs.router import router as cv_router
from server.database.base import test_connection, engine, Base
from server.modules.applications.router import router as app_router
from server.modules.ai_coach.router import router as ai_router
from server.modules.users.router import router as user_router

app = FastAPI(title="Career Mates API")

test_connection()

Base.metadata.create_all(bind=engine)

app.include_router(
    jobs_router,  
    prefix="/api/jobs",
    tags=["Jobs"]
)

app.include_router(
    cv_router,  
    prefix="/api/cvs",
    tags=["CVs"]
)

app.include_router(
    app_router,
    prefix="/api/applications",
    tags=["Applications"]
)

app.include_router(ai_router, prefix="/api")

app.include_router(user_router, prefix="/api/users", tags=["Users"])

@app.get("/")
def read_root():
    return {
        "status": "active",
        "message": "Welcome to Career Mates API!"
    }