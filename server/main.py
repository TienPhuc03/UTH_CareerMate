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

# Import config and logging
from core.logging_config import setup_logging, get_logger
from core.config import settings, display_settings
from core.redis_client import redis_client


# Setup logging
logger = setup_logging()

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
except Exception as e:
    logger.error(f"Failed to create tables: {e}")

# Test DB connection
test_connection()




# Đảm bảo Python tìm thấy các module khi chạy từ thư mục server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="CareerMate - AI Career Platform",
    description="AI-powered career platform for Vietnamese job seekers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS enabled for: {settings.allowed_origins_list}")

# Include routers
app.include_router(user_router, prefix="/api/Auth", tags=["Auth"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(cv_router, prefix="/api/cvs", tags=["CVs"])
app.include_router(app_router, prefix="/api/applications", tags=["Applications"])
app.include_router(ai_router, prefix="/api", tags=["AI Coach"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(recruiter_router, prefix="/api/recruiter", tags=["Recruiter"])

logger.info("All routers registered")


@app.on_event("startup")
def startup_event():
    """Application startup"""
    logger.info("=" * 70)
    logger.info(" CAREERMATE APPLICATION STARTUP")
    logger.info("=" * 70)
    
    # Display settings
    display_settings()
    
    # Check Redis
    redis_info = redis_client.get_info()
    if redis_info.get("status") == "connected":
        logger.info(f" Redis connected - {redis_info.get('total_keys', 0)} keys")
    else:
        logger.warning(" Redis not connected - caching disabled")

    logger.info("=" * 70)
    logger.info(" APPLICATION READY")
    logger.info(f" API Docs: http://localhost:8000/docs")
    logger.info("=" * 70)


@app.on_event("shutdown")
def shutdown_event():
    """Application shutdown"""
    logger.info(" Application shutting down...")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CareerMate API!",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
@app.get("/")
def root():
    return {"message": "Welcome to Career Mates API!", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Health check"""
    db_status = "healthy"
    try:
        test_connection()
    except:
        db_status = "unhealthy"
    
    redis_info = redis_client.get_info()
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "redis": redis_info.get("status", "unknown"),
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


@app.get("/api/system/cache-stats")
def get_cache_stats():
    """Get cache statistics"""
    return redis_client.get_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level=settings.LOG_LEVEL.lower()
    )



