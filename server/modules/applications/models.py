from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from server.database.base import Base 

class Application(Base): 
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    cv_id = Column(Integer, ForeignKey("cvs.id"), nullable=False)
    status = Column(String, default="PENDING")
    cover_letter = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())