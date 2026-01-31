
"""
Gemini AI Analyzer - Using google-genai SDK
"""
from google import genai
from google.genai import types
from core.config import settings
from core.logging_config import get_logger
from typing import Dict, Optional
import json
import time

logger = get_logger(__name__)
# Khởi tạo Client (Tự động lấy GEMINI_API_KEY từ biến môi trường hoặc config)
try:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Gemini Client: {e}")
    client = None

def analyze_cv_with_gemini(
    cv_text: str, 
    target_industry: Optional[str] = None
) -> Dict:
    """Analyze CV using Gemini AI (New SDK)"""
    start_time = time.time()
    
    if not client:
        return _create_fallback_analysis(cv_text[:500], "Client init failed")

    try:
        # Cắt ngắn text
        cv_text_limited = cv_text[:10000] 
        
        prompt = f"""Bạn là chuyên gia HR. Phân tích CV này.
Ngành: {target_industry or 'IT/Tech'}
CV:
{cv_text_limited}

Output JSON format:
{{
    "ats_score": 0-100,
    "overall_assessment": "...",
    "strengths": ["..."],
    "weaknesses": ["..."],
    "improvement_suggestions": ["..."],
    "skills_found": ["..."]
}}"""
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL, # Hardcode tên model chuẩn để tránh lỗi config cũ
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        duration = time.time() - start_time
        result_json = json.loads(response.text)
        
        logger.info(f"✅ Gemini analysis done. ATS: {result_json.get('ats_score')} ({duration:.2f}s)")
        return result_json
        
    except Exception as e:
        logger.error(f"Gemini analysis error: {e}")
        return _create_fallback_analysis(cv_text[:500], str(e))

def _create_fallback_analysis(cv_text: str, error: str = None) -> Dict:
    return {
        "ats_score": 0,
        "overall_assessment": "Hệ thống đang bảo trì AI.",
        "strengths": [],
        "weaknesses": ["Lỗi kết nối AI"],
        "error": error
    }

def generate_career_roadmap(
    cv_skills: str,
    target_role: str,
    current_level: str = "junior"
) -> Dict:
    """Generate career roadmap with google-genai SDK"""
    try:
        prompt = f"""Tạo lộ trình nghề nghiệp cho IT tại Việt Nam.

Kỹ năng hiện tại: {cv_skills}
Vị trí mục tiêu: {target_role}
Level: {current_level}

Trả về JSON (không markdown):
{{
    "target_role": "{target_role}",
    "estimated_timeline": "<thời gian>",
    "skill_gaps": [
        {{"skill": "<skill>", "priority": "<high/medium/low>", "reason": "<lý do>"}}
    ],
    "learning_path": [
        {{"phase": "1", "duration": "<thời gian>", "focus": "<trọng tâm>", "courses": ["<khóa học>"], "projects": ["<dự án>"]}}
    ],
    "certifications": ["<chứng chỉ 1>"],
    "next_steps": ["<hành động 1>", "<hành động 2>"],
    "tips": "<lời khuyên>"
}}"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        
        roadmap = json.loads(text)
        logger.info(f"✅ Roadmap generated for {target_role}")
        return roadmap
        
    except Exception as e:
        logger.error(f"Roadmap error: {e}")
        return {
            "target_role": target_role,
            "estimated_timeline": "6-12 tháng",
            "skill_gaps": [],
            "learning_path": [],
            "certifications": [],
            "next_steps": ["Cập nhật CV", "Học thêm kỹ năng"],
            "tips": "Học từng kỹ năng một cách có hệ thống"
        }


def compare_cv_with_job(cv_text: str, job_description: str) -> Dict:
    """Compare CV with job using google-genai SDK"""
    try:
        prompt = f"""So sánh CV với JD và trả về JSON (không markdown).

Job:
{job_description[:1500]}

CV:
{cv_text[:3000]}

JSON:
{{
    "match_score": <0-100>,
    "matching_skills": ["<skill1>"],
    "missing_requirements": ["<thiếu 1>"],
    "recommendation": "<nên ứng tuyển hay cải thiện>",
    "cover_letter_tips": ["<tip1>", "<tip2>"]
}}"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        
        result = json.loads(text)
        logger.info(f"✅ CV-Job match: {result.get('match_score')}")
        return result
        
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return {
            "match_score": 50,
            "matching_skills": [],
            "missing_requirements": [],
            "recommendation": "Không thể phân tích",
            "cover_letter_tips": []
        }


def _create_fallback_analysis(cv_text: str, error: str = None) -> Dict:
    """Fallback analysis"""
    skills = ['python', 'java', 'javascript', 'sql', 'react']
    found = [s for s in skills if s in cv_text.lower()]
    
    return {
        "ats_score": 50,
        "overall_assessment": "Phân tích AI tạm thời không khả dụng",
        "strengths": ["CV đã tải lên thành công"],
        "weaknesses": ["Không thể phân tích chi tiết"],
        "skills_found": found,
        "missing_skills": ["docker", "kubernetes"],
        "improvement_suggestions": [
            "Thêm kỹ năng cụ thể",
            "Bổ sung thành tích",
            "Cải thiện format"
        ],
        "keyword_optimization": {
            "current_keywords": found[:2],
            "recommended_keywords": ["agile", "git"]
        },
        "career_advice": "Tập trung phát triển kỹ năng chuyên môn",
        "error": error
    }