from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database.base import Base 

class Application(Base): 
    __tablename__ = "applications"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    cv_id = Column(Integer, ForeignKey("cvs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # NEW
    # Application Content
    cover_letter = Column(Text, nullable=True)
    # Status Tracking - ENHANCED
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    # Possible values: PENDING, REVIEWING, INTERVIEWED, ACCEPTED, REJECTED
    # AI Matching
    matching_score = Column(Float, nullable=True)   # Score from AI job matching (0-100)
    matched_skills = Column(Text, nullable=True)    # Comma-separated matched skills
    missing_skills = Column(Text, nullable=True)    # Comma-separated missing skills
    # Recruiter Notes
    recruiter_notes = Column(Text, nullable=True)   # Private notes from recruiter
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)  #When status changed
    
    def __repr__(self):
        return f"<Application Job#{self.job_id} CV#{self.cv_id} - {self.status}>"