from fastapi import FastAPI
import uvicorn

# Import engine từ session.py và Base từ base.p

from database.base import Base
from database.session import engine

# Import models để SQLAlchemy nhận diện bảng cần tạo
from modules.jobs import router as job_router

# Tự động tạo bảng khi server khởi động
# Trong file main.py
try:
    # SQLAlchemy cần load CẢ HAI models này để biết mối liên kết khóa ngoại
    from modules.users import models as user_models 
    from modules.jobs import models as job_models
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables (Users & Jobs) created successfully!")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
app = FastAPI(title="CareerMate – AI-Powered Job Companion")

# Root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Welcome to CareerMate API System"}

# Include routers from different modules
# Prefix will make URLs like: http://localhost:8000/api/v1/jobs/
app.include_router(job_router.router, prefix="/api/v1", tags=["Jobs Management"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)