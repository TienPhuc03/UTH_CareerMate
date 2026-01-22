from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from database.base import Base

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    salary_range = Column(String(100))
    job_type = Column(String(50))
    created_at = Column(TIMESTAMP)
