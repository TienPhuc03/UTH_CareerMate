from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from database.base import Base

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)    
    # Recruiter Info 
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    recruiter_email = Column(String(255), nullable=True, index=True)
    company_name = Column(String(255), nullable=True)
    # Job Info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # Job Details
    requirements = Column(Text, nullable=True)      # Required skills/experience
    benefits = Column(Text, nullable=True)          # Company benefits
    location = Column(String(255), nullable=True)   # Work location
    job_type = Column(String(50), default="full_time")  # full_time, part_time, internship, remote
    salary_range = Column(String(100), nullable=True)
    # Status - NEW
    status = Column(String(50), default="active")   # active, closed, draft
    is_approved = Column(Boolean, default=True)     # For admin approval workflow
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # NEW - Job expiry date
    
    def __repr__(self):
        return f"<Job {self.title} - {self.company_name}>"
