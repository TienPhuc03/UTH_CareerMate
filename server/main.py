
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.base import Base, engine, test_connection
from modules.users.router import router as user_router

# Create all tables
Base.metadata.create_all(bind=engine)

# Test database connection
test_connection()

# Initialize FastAPI app
app = FastAPI(
    title="Career Mates",
    description="API for user registration and authentication",
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