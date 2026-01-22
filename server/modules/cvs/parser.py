from typing import Dict, Any
import PyPDF2
import docx
import re

def parse_cv_file(file_path: str, file_ext: str) -> Dict[str, Any]:
    """
    Parse CV file (PDF or DOCX) and extract information
    
    Args:
        file_path: Path to the CV file
        file_ext: File extension (pdf or docx)
        
    Returns:
        Dictionary with extracted information
    """
    text = ""
    
    if file_ext.lower() == 'pdf':
        # Parse PDF
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    
    elif file_ext.lower() in ['docx', 'doc']:
        # Parse DOCX
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    # Extract basic information (simple regex)
    full_name = extract_name(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    
    return {
        "raw_text": text.strip(),
        "full_name": full_name,
        "phone": phone,
        "skills": skills,
        "file_type": file_ext.lower()
    }


def extract_name(text: str) -> str:
    """Extract name from CV text (simple heuristic)"""
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if len(line) > 5 and len(line) < 50 and not any(char.isdigit() for char in line):
            return line
    return "Unknown"


def extract_phone(text: str) -> str:
    """Extract phone number from CV text"""
    phone_pattern = r'(\+?84|0)[\s-]?\d{2,3}[\s-]?\d{3}[\s-]?\d{3,4}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None


def extract_skills(text: str) -> list:
    """Extract skills from CV text"""
    common_skills = [
        'python', 'java', 'javascript', 'react', 'nodejs', 'sql', 'mongodb',
        'docker', 'kubernetes', 'aws', 'git', 'html', 'css', 'typescript',
        'fastapi', 'django', 'flask', 'machine learning', 'ai', 'data analysis'
    ]
    
    text_lower = text.lower()
    found_skills = [skill for skill in common_skills if skill in text_lower]
    return found_skills