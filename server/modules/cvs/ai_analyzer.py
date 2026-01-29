"""
Gemini AI Analyzer - SYNC VERSION
"""
# import google.generativeai as genai
# from core.config import settings
# from core.logging_config import get_logger
# from typing import Dict, Optional
# import json
# import time

# logger = get_logger(__name__)

# # Configure Gemini
# genai.configure(api_key=settings.GEMINI_API_KEY)


# def analyze_cv_with_gemini(
#     cv_text: str, 
#     target_industry: Optional[str] = None
# ) -> Dict:
#     """
#     Analyze CV using Gemini AI (SYNC)
    
#     Args:
#         cv_text: CV contentv
#         target_industry: Target industry
        
#     Returns:
#         Analysis results
#     """
#     start_time = time.time()
    
#     try:
#         cv_text_limited = cv_text[:4000]
        
#         prompt = f"""Bạn là chuyên gia HR tại Việt Nam. Phân tích CV này và trả về JSON.

# Ngành mục tiêu: {target_industry or 'IT/Tech'}

# CV:
# {cv_text_limited}

# Trả về JSON (không có markdown, chỉ JSON thuần):
# {{
#     "ats_score": <số 0-100>,
#     "overall_assessment": "<đánh giá tổng quan bằng tiếng Việt>",
#     "strengths": ["<điểm mạnh 1>", "<điểm mạnh 2>", "<điểm mạnh 3>"],
#     "weaknesses": ["<điểm yếu 1>", "<điểm yếu 2>"],
#     "skills_found": ["<skill1>", "<skill2>"],
#     "missing_skills": ["<skill thiếu 1>", "<skill thiếu 2>"],
#     "improvement_suggestions": ["<gợi ý 1>", "<gợi ý 2>", "<gợi ý 3>"],
#     "keyword_optimization": {{
#         "current_keywords": ["<từ khóa 1>", "<từ khóa 2>"],
#         "recommended_keywords": ["<từ khóa nên thêm 1>", "<từ khóa nên thêm 2>"]
#     }},
#     "career_advice": "<lời khuyên nghề nghiệp>"
# }}"""

#         model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
#         response = model.generate_content(
#             prompt,
#             generation_config={
#                 "temperature": 0.7,
#                 "top_p": 0.95,
#                 "max_output_tokens": 2048,
#             }
#         )
        
#         duration = time.time() - start_time
#         response_text = response.text.strip()
        
#         # Clean markdown
#         if "```json" in response_text:
#             response_text = response_text.split("```json")[1].split("```")[0].strip()
#         elif response_text.startswith("```"):
#             response_text = response_text.replace("```", "").strip()
        
#         # Parse JSON
#         analysis = json.loads(response_text)
#         logger.info(f"✅ Gemini analysis done. ATS: {analysis.get('ats_score')} ({duration:.2f}s)")
#         return analysis
        
#     except json.JSONDecodeError as e:
#         logger.error(f"JSON parse error: {e}")
#         return _create_fallback_analysis(cv_text[:500])
#     except Exception as e:
#         logger.error(f"Gemini error: {e}")
#         return _create_fallback_analysis(cv_text[:500], str(e))


# def generate_career_roadmap(
#     cv_skills: str,
#     target_role: str,
#     current_level: str = "junior"
# ) -> Dict:
#     """Generate career roadmap (SYNC)"""
#     try:
#         prompt = f"""Tạo lộ trình nghề nghiệp cho IT tại Việt Nam.

# Kỹ năng hiện tại: {cv_skills}
# Vị trí mục tiêu: {target_role}
# Level: {current_level}

# Trả về JSON (không markdown):
# {{
#     "target_role": "{target_role}",
#     "estimated_timeline": "<thời gian>",
#     "skill_gaps": [
#         {{"skill": "<skill>", "priority": "<high/medium/low>", "reason": "<lý do>"}}
#     ],
#     "learning_path": [
#         {{"phase": "1", "duration": "<thời gian>", "focus": "<trọng tâm>", "courses": ["<khóa học>"], "projects": ["<dự án>"]}}
#     ],
#     "certifications": ["<chứng chỉ 1>"],
#     "next_steps": ["<hành động 1>", "<hành động 2>"],
#     "tips": "<lời khuyên>"
# }}"""

#         model = genai.GenerativeModel(settings.GEMINI_MODEL)
#         response = model.generate_content(prompt)
        
#         text = response.text.strip()
#         if "```json" in text:
#             text = text.split("```json")[1].split("```")[0].strip()
        
#         roadmap = json.loads(text)
#         logger.info(f"✅ Roadmap generated for {target_role}")
#         return roadmap
        
#     except Exception as e:
#         logger.error(f"Roadmap error: {e}")
#         return {
#             "target_role": target_role,
#             "estimated_timeline": "6-12 tháng",
#             "skill_gaps": [],
#             "learning_path": [],
#             "certifications": [],
#             "next_steps": ["Cập nhật CV", "Học thêm kỹ năng"],
#             "tips": "Học từng kỹ năng một cách có hệ thống"
#         }


# def compare_cv_with_job(cv_text: str, job_description: str) -> Dict:
#     """Compare CV with job (SYNC)"""
#     try:
#         prompt = f"""So sánh CV với JD và trả về JSON (không markdown).

# Job:
# {job_description[:1500]}

# CV:
# {cv_text[:3000]}

# JSON:
# {{
#     "match_score": <0-100>,
#     "matching_skills": ["<skill1>"],
#     "missing_requirements": ["<thiếu 1>"],
#     "recommendation": "<nên ứng tuyển hay cải thiện>",
#     "cover_letter_tips": ["<tip1>", "<tip2>"]
# }}"""

#         model = genai.GenerativeModel(settings.GEMINI_MODEL)
#         response = model.generate_content(prompt)
        
#         text = response.text.strip()
#         if "```json" in text:
#             text = text.split("```json")[1].split("```")[0].strip()
        
#         result = json.loads(text)
#         logger.info(f"✅ CV-Job match: {result.get('match_score')}")
#         return result
        
#     except Exception as e:
#         logger.error(f"Comparison error: {e}")
#         return {
#             "match_score": 50,
#             "matching_skills": [],
#             "missing_requirements": [],
#             "recommendation": "Không thể phân tích",
#             "cover_letter_tips": []
#         }


# def _create_fallback_analysis(cv_text: str, error: str = None) -> Dict:
#     """Fallback analysis"""
#     skills = ['python', 'java', 'javascript', 'sql', 'react']
#     found = [s for s in skills if s in cv_text.lower()]
    
#     return {
#         "ats_score": 50,
#         "overall_assessment": "Phân tích AI tạm thời không khả dụng",
#         "strengths": ["CV đã tải lên thành công"],
#         "weaknesses": ["Không thể phân tích chi tiết"],
#         "skills_found": found,
#         "missing_skills": ["docker", "kubernetes"],
#         "improvement_suggestions": [
#             "Thêm kỹ năng cụ thể",
#             "Bổ sung thành tích",
#             "Cải thiện format"
#         ],
#         "keyword_optimization": {
#             "current_keywords": found[:2],
#             "recommended_keywords": ["agile", "git"]
#         },
#         "career_advice": "Tập trung phát triển kỹ năng chuyên môn",
#         "error": error
#     }
import google.generativeai as genai
from core.config import settings
from core.logging_config import get_logger
from typing import Dict, Optional
import json
import time

logger = get_logger(__name__)

# Configure Gemini - FIXED: Use gemini-1.5-flash
genai.configure(api_key=settings.GEMINI_API_KEY)

# CRITICAL FIX: Use the exact model name that Google expects
GEMINI_MODEL = "gemini-1.5-flash"  # This is the correct name for API v1


def analyze_cv_with_gemini(
    cv_text: str, 
    target_industry: Optional[str] = None
) -> Dict:
    """
    Analyze CV using Gemini AI (SYNC)
    
    Args:
        cv_text: CV content
        target_industry: Target industry
        
    Returns:
        Analysis results
    """
    start_time = time.time()
    
    try:
        cv_text_limited = cv_text[:4000]
        
        prompt = f"""Bạn là chuyên gia HR tại Việt Nam. Phân tích CV này và trả về JSON.

Ngành mục tiêu: {target_industry or 'IT/Tech'}

CV:
{cv_text_limited}

Trả về JSON (không có markdown, chỉ JSON thuần):
{{
    "ats_score": <số 0-100>,
    "overall_assessment": "<đánh giá tổng quan bằng tiếng Việt>",
    "strengths": ["<điểm mạnh 1>", "<điểm mạnh 2>", "<điểm mạnh 3>"],
    "weaknesses": ["<điểm yếu 1>", "<điểm yếu 2>"],
    "skills_found": ["<skill1>", "<skill2>"],
    "missing_skills": ["<skill thiếu 1>", "<skill thiếu 2>"],
    "improvement_suggestions": ["<gợi ý 1>", "<gợi ý 2>", "<gợi ý 3>"],
    "keyword_optimization": {{
        "current_keywords": ["<từ khóa 1>", "<từ khóa 2>"],
        "recommended_keywords": ["<từ khóa nên thêm 1>", "<từ khóa nên thêm 2>"]
    }},
    "career_advice": "<lời khuyên nghề nghiệp>"
}}"""

        # FIXED: Use hardcoded model name instead of settings
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 2048,
            }
        )
        
        duration = time.time() - start_time
        response_text = response.text.strip()
        
        # Clean markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Parse JSON
        analysis = json.loads(response_text)
        logger.info(f"✅ Gemini analysis done. ATS: {analysis.get('ats_score')} ({duration:.2f}s)")
        return analysis
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return _create_fallback_analysis(cv_text[:500])
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return _create_fallback_analysis(cv_text[:500], str(e))


def generate_career_roadmap(
    cv_skills: str,
    target_role: str,
    current_level: str = "junior"
) -> Dict:
    """Generate career roadmap (SYNC)"""
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

        # FIXED: Use hardcoded model name
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
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
    """Compare CV with job (SYNC)"""
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

        # FIXED: Use hardcoded model name
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
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