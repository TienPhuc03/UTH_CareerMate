# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from database.session import get_db
# from modules.applications.models import Application
# from modules.ai_coach.service import generate_feedback 

# router = APIRouter(prefix="/ai-coach", tags=["AI Coach"])

# @router.post("/analyze/{application_id}")
# def analyze_application(application_id: int, db: Session = Depends(get_db)):
#     app = db.query(Application).filter(Application.id == application_id).first()
    
#     if not app:
#         return {"error": "Application không tồn tại"}

#     feedback = generate_feedback(
#         cv_skills=app.cv.skills, 
#         job_description=app.job.description
#     )
    
#     return {
#         "application_id": application_id,
#         "candidate": app.cv.full_name,
#         "job_title": app.job.title,
#         "analysis": feedback
#     }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from pydantic import BaseModel
from typing import List, Optional, Dict
import json

router = APIRouter(prefix="/ai-coach", tags=["AI Coach"])

# ============= SCHEMAS =============
class ChatMessage(BaseModel):
    message: str
    user_email: str
    history: Optional[List[Dict]] = []

class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = []

class CVAnalysisRequest(BaseModel):
    cv_text: str
    user_email: str

class CVAnalysisResponse(BaseModel):
    overall_score: int
    ats_compatible: bool
    skills_found: List[str]
    skills_missing: List[str]
    suggestions: List[str]

class JobRecommendationRequest(BaseModel):
    user_email: str
    skills: List[str]
    experience_level: str = "junior"

class JobRecommendation(BaseModel):
    job_id: int
    title: str
    company: str
    matching_score: int
    matched_skills: List[str]
    missing_skills: List[str]

# ============= AI CHAT ENDPOINT =============
@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatMessage, db: Session = Depends(get_db)):
    """
    Career AI Chatbot - Trả lời câu hỏi về CV, career, skills
    """
    try:
        message = request.message.lower()
        response_text = ""
        suggestions = []
        
        # Simple keyword-based responses (có thể thay bằng OpenAI API sau)
        if "cv" in message or "resume" in message:
            response_text = """
**Để tạo CV chuyên nghiệp cho sinh viên mới ra trường:**

• **Thông tin cá nhân**: Họ tên, email, số điện thoại, LinkedIn
• **Mục tiêu nghề nghiệp**: Ngắn gọn, rõ ràng (2-3 câu)
• **Học vấn**: Trường, chuyên ngành, GPA (nếu > 3.0)
• **Kỹ năng**: Liệt kê kỹ năng kỹ thuật cụ thể
• **Dự án**: 2-3 dự án nổi bật với mô tả ngắn gọn
• **Kinh nghiệm**: Thực tập, part-time (nếu có)

**Lưu ý quan trọng:**
✓ Sử dụng số liệu cụ thể (tăng 30%, giảm 40%...)
✓ Format đơn giản, dễ đọc (ATS-friendly)
✓ Tối đa 1-2 trang
✓ Không có lỗi chính tả

Bạn muốn tôi phân tích CV hiện tại của bạn không?
            """
            suggestions = [
                "Phân tích CV của tôi",
                "Tìm việc phù hợp",
                "Lộ trình học Backend"
            ]
            
        elif "việc làm" in message or "job" in message or "tìm việc" in message:
            response_text = """
**Để tìm việc làm phù hợp:**

• **Xác định kỹ năng của bạn**: Python, FastAPI, SQL, React...
• **Chọn level phù hợp**: Intern, Junior, Mid-level
• **Địa điểm**: Remote, TP.HCM, Hà Nội...

**Các nguồn tuyển dụng tốt:**
✓ LinkedIn Jobs
✓ ITviec.com
✓ TopCV.vn
✓ CareerBuilder

Tôi có thể phân tích CV của bạn và đề xuất việc làm phù hợp với AI matching score!

Bạn muốn xem danh sách việc làm được đề xuất không?
            """
            suggestions = [
                "Xem việc làm đề xuất",
                "Phân tích CV của tôi",
                "Chuẩn bị phỏng vấn"
            ]
            
        elif "phỏng vấn" in message or "interview" in message:
            response_text = """
**Chuẩn bị phỏng vấn Backend Developer:**

**1. Kỹ thuật cơ bản:**
• HTTP methods (GET, POST, PUT, DELETE)
• RESTful API design
• Database (SQL vs NoSQL)
• Authentication (JWT, OAuth)

**2. Câu hỏi thường gặp:**
• Giải thích về MVC pattern
• Sự khác biệt giữa SQL và NoSQL
• Cách tối ưu API performance
• Security best practices

**3. Soft skills:**
• Kỹ năng giao tiếp
• Làm việc nhóm
• Giải quyết vấn đề

Bạn muốn tôi mô phỏng buổi phỏng vấn không?
            """
            suggestions = [
                "Câu hỏi phỏng vấn Python",
                "Câu hỏi về FastAPI",
                "Tips phỏng vấn"
            ]
            
        elif "lộ trình" in message or "roadmap" in message or "học" in message:
            response_text = """
**Lộ trình học Backend Developer (6-12 tháng):**

**Tháng 1-2: Nền tảng**
• Python cơ bản
• Git & GitHub
• Linux command line

**Tháng 3-4: Web Backend**
• FastAPI/Django
• PostgreSQL/MySQL
• RESTful API

**Tháng 5-6: Advanced**
• Authentication & Security
• Redis (Caching)
• Docker basics

**Tháng 7-8: DevOps**
• Docker & Docker Compose
• CI/CD basics
• AWS/GCP basics

**Tháng 9-12: Projects & Apply**
• 3-5 dự án portfolio
• Đóng góp open source
• Ứng tuyển việc làm

Bạn muốn lộ trình chi tiết cho vị trí nào?
            """
            suggestions = [
                "Lộ trình Frontend",
                "Lộ trình Data Science",
                "Khóa học đề xuất"
            ]
            
        else:
            response_text = """
Xin chào! Tôi là Career AI Coach. Tôi có thể giúp bạn:

• **Tạo & phân tích CV** chuyên nghiệp
• **Tìm việc làm** phù hợp với kỹ năng
• **Lộ trình học tập** cho từng vị trí
• **Chuẩn bị phỏng vấn** hiệu quả

Bạn muốn hỏi về vấn đề gì?
            """
            suggestions = [
                "Tạo CV chuyên nghiệp",
                "Tìm việc làm",
                "Lộ trình học Backend",
                "Chuẩn bị phỏng vấn"
            ]
        
        return ChatResponse(
            response=response_text.strip(),
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# ============= CV ANALYSIS ENDPOINT =============
@router.post("/analyze-cv", response_model=CVAnalysisResponse)
async def analyze_cv(request: CVAnalysisRequest, db: Session = Depends(get_db)):
    """
    Phân tích CV với AI - Mock response
    """
    try:
        cv_text = request.cv_text.lower()
        
        # Extract skills
        all_skills = ["python", "fastapi", "javascript", "react", "sql", "postgresql", 
                     "docker", "git", "aws", "mongodb", "nodejs", "typescript"]
        
        skills_found = [skill for skill in all_skills if skill in cv_text]
        skills_missing = [skill for skill in all_skills if skill not in cv_text and skill in ["docker", "aws", "typescript"]]
        
        # Calculate score
        score = min(95, 60 + len(skills_found) * 5)
        
        # ATS check
        ats_compatible = "email" in cv_text and "phone" in cv_text
        
        # Suggestions
        suggestions = [
            "Thêm số liệu định lượng (tăng 30%, giảm 40%...)",
            "Sử dụng action verbs: Developed, Implemented, Optimized",
            "Thêm section 'Projects' với link GitHub",
            "Format CV theo chuẩn ATS (không dùng table phức tạp)",
            f"Bổ sung kỹ năng: {', '.join(skills_missing[:3])}"
        ]
        
        return CVAnalysisResponse(
            overall_score=score,
            ats_compatible=ats_compatible,
            skills_found=skills_found,
            skills_missing=skills_missing,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


# ============= JOB RECOMMENDATIONS ENDPOINT =============
@router.post("/job-recommendations", response_model=List[JobRecommendation])
async def recommend_jobs(request: JobRecommendationRequest, db: Session = Depends(get_db)):
    """
    AI Job Matching - Đề xuất việc làm với matching score
    """
    try:
        user_skills = [s.lower() for s in request.skills]
        
        # Mock job data (trong thực tế query từ database)
        mock_jobs = [
            {
                "job_id": 1,
                "title": "Frontend Developer",
                "company": "Công ty Công nghệ ABC",
                "required_skills": ["react", "javascript", "tailwind", "html", "css"],
                "salary": "15-25tr",
                "location": "TP.HCM"
            },
            {
                "job_id": 2,
                "title": "Backend Developer",
                "company": "FPT Software",
                "required_skills": ["python", "fastapi", "postgresql", "docker", "aws"],
                "salary": "18-30tr",
                "location": "TP.HCM"
            },
            {
                "job_id": 3,
                "title": "Fullstack Developer",
                "company": "VNG Corporation",
                "required_skills": ["react", "nodejs", "mongodb", "docker", "aws"],
                "salary": "20-35tr",
                "location": "TP.HCM"
            },
            {
                "job_id": 4,
                "title": "Data Analyst",
                "company": "Tiki Corporation",
                "required_skills": ["python", "sql", "powerbi", "excel"],
                "salary": "12-22tr",
                "location": "TP.HCM"
            }
        ]
        
        # Calculate matching scores
        recommendations = []
        for job in mock_jobs:
            required = set(job["required_skills"])
            user = set(user_skills)
            
            matched = list(required.intersection(user))
            missing = list(required.difference(user))
            
            # Calculate score: (matched skills / total required) * 100
            score = int((len(matched) / len(required)) * 100) if required else 0
            
            # Add bonus for experience level
            if request.experience_level == "senior":
                score = min(100, score + 10)
            
            recommendations.append(JobRecommendation(
                job_id=job["job_id"],
                title=job["title"],
                company=job["company"],
                matching_score=score,
                matched_skills=matched,
                missing_skills=missing
            ))
        
        # Sort by matching score
        recommendations.sort(key=lambda x: x.matching_score, reverse=True)
        
        return recommendations[:9]  # Top 9 jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")