from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class CVCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None  

class CVResponse(CVCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    ats_score: Optional[float] = None
    ai_feedback: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class CVAnalysisResult(BaseModel):
    analysis_status: str = "success"
    ats_score: float = 0
    overall_assessment: str = ""
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    skills_found: list[str] = Field(default_factory=list)
    error: Optional[str] = None


class CVUploadParsedData(BaseModel):
    full_name: Optional[str] = None
    email: EmailStr
    skills_count: int = 0


class CVUploadFileInfo(BaseModel):
    filename: str
    size_kb: float


class CVUploadResponse(BaseModel):
    cv_id: int
    message: str
    analysis_status: str
    analysis_error: Optional[str] = None
    parsed_data: CVUploadParsedData
    ats_score: Optional[float] = None
    ai_analysis: Optional[CVAnalysisResult] = None
    file_info: CVUploadFileInfo

