def generate_feedback(cv_skills: str, job_description: str):
    
    cv_skills = cv_skills.lower() if cv_skills else ""
    job_desc = job_description.lower() if job_description else ""
    
    keywords = ["python", "fastapi", "sql", "react", "javascript", "docker", "java", "html", "css"]
    found = [word for word in keywords if word in job_desc and word in cv_skills]
    missing = [word for word in keywords if word in job_desc and word not in cv_skills]
    
    total_relevant = len(found) + len(missing)
    score = (len(found) / total_relevant) * 100 if total_relevant > 0 else 0
    
    return {
        "matching_score": round(score, 2),
        "found_skills": found,
        "missing_skills": missing,
        "advice": "Hồ sơ của bạn rất tốt !" if score > 70 else "Hãy thêm các kỹ năng thiếu để có cơ hội trúng tuyển."
    }