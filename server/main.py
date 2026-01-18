
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.base import Base, engine, test_connection
from modules.users.router import router as user_router
from modules.jobs.router import router as jobs_router 
from modules.cvs.router import router as cv_router
from modules.applications.router import router as app_router
from modules.ai_coach.router import router as ai_router
from modules.admin.router import router as admin_router
import sys
import os
from fastapi import FastAPI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



# Create all tables
Base.metadata.create_all(bind=engine)

# Test database connection
test_connection()

# Initialize FastAPI app
app = FastAPI(
    title="Career Mates",
    description="App for job seekers and employers",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, prefix="/api/Auth", tags=["Auth"])

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

app.include_router(
    admin_router, 
    prefix="/api/admin", 
    tags=["Admin"]
)

app.include_router(admin_router, prefix="/api")

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Career Mates API!",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




