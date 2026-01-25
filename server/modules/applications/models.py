from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database.base import Base

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cv_id = Column(Integer, ForeignKey("cvs.id"), nullable=True)
    status = Column(String, default="PENDING")  # PENDING, REVIEWING, INTERVIEWED, ACCEPTED, REJECTED
    notes = Column(Text, nullable=True)
    cover_letter = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())