from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.base import Base, engine, test_connection
from modules.users.router import router as user_router
from modules.jobs.router import router as jobs_router 
from modules.cvs.router import router as cv_router
from modules.applications.router import router as app_router
from modules.ai_coach.router import router as ai_router
from modules.admin.router import router as admin_router
from modules.recruiter.router import router as recruiter_router

import sys
import os

# Đảm bảo Python tìm thấy các module khi chạy từ thư mục server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Khởi tạo DB (Dòng này sẽ tự tạo bảng nếu chưa có)
Base.metadata.create_all(bind=engine)
test_connection()

app = FastAPI(
    title="Career Mates",
    description="App for job seekers and employers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- KHU VỰC INCLUDE ROUTERS ---
app.include_router(user_router, prefix="/api/Auth", tags=["Auth"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(cv_router, prefix="/api/cvs", tags=["CVs"])
app.include_router(app_router, prefix="/api/applications", tags=["Applications"])
app.include_router(ai_router, prefix="/api", tags=["AI Coach"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(recruiter_router, prefix="/api/recruiter", tags=["Recruiter"])

@app.get("/")
def root():
    return {"message": "Welcome to Career Mates API!", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)