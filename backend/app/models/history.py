import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(String(50), primary_key=True, default=lambda: f"hist-{int(datetime.utcnow().timestamp())}")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    job_title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    match_score = Column(Integer, nullable=False, default=80)
    ats_score = Column(Integer, nullable=False, default=85)
    status = Column(String(50), default="Strong Match")
    missing_count = Column(Integer, default=0)
    matched_count = Column(Integer, default=0)
    
    skills = Column(JSON, default=list)
    full_result = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analysis_history")
