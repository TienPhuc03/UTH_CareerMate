from sqlalchemy import Column, Integer, Text, ForeignKey, Float
from server.database.base import Base

class AICoachFeedback(Base):
    __tablename__ = "ai_coach_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    matching_score = Column(Float)  # Điểm khớp (0-100)
    feedback_text = Column(Text)    # Lời khuyên từ AI
    suggested_skills = Column(Text) # Kỹ năng cần thêm