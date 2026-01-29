
import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add server directory to path
sys.path.append(os.path.join(os.getcwd(), "server"))

from main import app
from database.base import Base
from database.session import get_db
from core.dependencies import require_recruiter
from modules.users.models import User

# Setup in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Mock recruiter user
mock_recruiter = User(
    id=999,
    email="recruiter@test.com",
    role="recruiter",
    is_active=True
)

def override_require_recruiter():
    return mock_recruiter

# Apply overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[require_recruiter] = override_require_recruiter

client = TestClient(app)

def test_create_job_linked_to_recruiter():
    payload = {
        "title": "Senior Python Developer",
        "description": "Great job",
        "location": "Ho Chi Minh",
        "salary_range": "1000-2000",
        "company_name": "Test Company Corp"
    }
    
    response = client.post("/api/jobs/", json=payload)
    
    assert response.status_code == 200, f"Failed: {response.text}"
    data = response.json()
    
    print("\n--- Job Creation Test Results ---")
    print(f"Job ID: {data.get('id')}")
    print(f"Recruiter ID: {data.get('recruiter_id')}")
    print(f"Recruiter Email: {data.get('recruiter_email')}")
    print(f"Company Name: {data.get('company_name')}")
    
    # Verification
    assert data["recruiter_id"] == 999
    assert data["recruiter_email"] == "recruiter@test.com"
    assert data["company_name"] == "Test Company Corp" # Assumes schema update worked
    
    print("SUCCESS: Job is correctly linked to the recruiter!")

if __name__ == "__main__":
    try:
        test_create_job_linked_to_recruiter()
    except AssertionError as e:
        print(f"FAILURE: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
