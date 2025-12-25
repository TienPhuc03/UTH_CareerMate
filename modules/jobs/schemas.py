from pydantic import BaseModel
from typing import Optional, List

class JobBase(BaseModel):
    title: str
    description: str
    company_name: str
    location: str
    salary_range: Optional[str] = None
    required_skills: str

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    ai_matching_score: Optional[float] = 0.0 # UC 36: Job-Matching Scores

    class Config:
        from_attributes = True