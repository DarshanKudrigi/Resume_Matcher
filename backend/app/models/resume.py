import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(50), primary_key=True, default=lambda: f"res-{uuid.uuid4().hex[:8]}")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False, default="Untitled Resume")
    template = Column(String(50), default="modern")  # 'modern' | 'classic' | 'minimal'
    target_role = Column(String(200), nullable=True, default="")
    ats_score = Column(Integer, default=85)
    
    # Structured resume data matching frontend schema
    personal_info = Column(JSON, default=dict)
    summary = Column(Text, nullable=True, default="")
    education = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    skills = Column(JSON, default=dict)
    certifications = Column(JSON, default=list)
    achievements = Column(JSON, default=list)
    tags = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String(50), primary_key=True, default=lambda: f"file-{uuid.uuid4().hex[:8]}")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(String(50), default="1.0 MB")
    content_type = Column(String(100), default="application/pdf")
    status = Column(String(50), default="ready")
    
    extracted_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
