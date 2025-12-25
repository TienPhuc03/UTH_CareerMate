from typing import List
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from database.base import Base  # Giả định bạn đã có file base.py định nghĩa Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False) # UC 23: Search Jobs
    description = Column(Text, nullable=False)
    company_name = Column(String(255)) # UC 19: Company Satisfaction
    location = Column(String(100))
    salary_range = Column(String(100))
    required_skills = Column(Text) # Phục vụ AI Matching Score
    recruiter_id = Column(Integer, ForeignKey("users.id")) # UC 30: Post Jobs