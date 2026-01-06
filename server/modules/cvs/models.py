#bảng CVresults lưu kết quả trích xuất từ file CV
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from server.database.base import Base

class CV(Base):
    __tablename__ = "cvs"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    skills = Column(Text)
    experience = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
