import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from app.database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(String(50), primary_key=True, default=lambda: f"job-{uuid.uuid4().hex[:8]}")
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(150), nullable=True, default="")
    url = Column(String(500), nullable=True, default="")
    experience = Column(String(100), nullable=True, default="")
    description = Column(Text, nullable=False)
    
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
