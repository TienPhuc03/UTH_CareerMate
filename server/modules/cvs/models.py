#bảng CVresults lưu kết quả trích xuất từ file CV
from sqlalchemy import JSON, Column, Float, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database.base import Base

class CV(Base):
    __tablename__ = "cvs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    # User Reference - NEW
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    
    # CV Content
    skills = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    education = Column(Text, nullable=True)  # NEW
    
    # File Info - NEW FIELDS
    file_path = Column(String(500), nullable=True) 
    file_name = Column(String(255), nullable=True) 
    file_type = Column(String(10), nullable=True)  
    
    # AI Analysis Results - NEW FIELDS
    ats_score = Column(Float, nullable=True)  
    ai_feedback = Column(JSON, nullable=True)     
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self):
        return f"<CV {self.full_name} - ATS: {self.ats_score}>"
