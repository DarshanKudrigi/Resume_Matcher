import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=True, default="")
    location = Column(String(150), nullable=True, default="")
    headline = Column(String(255), nullable=True, default="")
    avatar = Column(String(20), nullable=True, default="DS")
    linkedin = Column(String(255), nullable=True, default="")
    github = Column(String(255), nullable=True, default="")
    portfolio = Column(String(255), nullable=True, default="")
    college = Column(String(255), nullable=True, default="")
    degree = Column(String(255), nullable=True, default="")
    graduation_year = Column(String(20), nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
