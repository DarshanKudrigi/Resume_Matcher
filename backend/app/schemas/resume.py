from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class PersonalInfo(BaseModel):
    fullName: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    headline: str = ""

class EducationItem(BaseModel):
    id: str = ""
    institution: str = ""
    degree: str = ""
    location: str = ""
    startDate: str = ""
    endDate: str = ""
    score: str = ""

class ExperienceItem(BaseModel):
    id: str = ""
    role: str = ""
    company: str = ""
    location: str = ""
    startDate: str = ""
    endDate: str = ""
    bullets: List[str] = []

class ProjectItem(BaseModel):
    id: str = ""
    name: str = ""
    tech: str = ""
    link: str = ""
    bullets: List[str] = []

class SkillsData(BaseModel):
    languages: List[str] = []
    frameworks: List[str] = []
    tools: List[str] = []
    concepts: List[str] = []

class CertificationItem(BaseModel):
    id: str = ""
    name: str = ""
    issuer: str = ""
    year: str = ""

class AchievementItem(BaseModel):
    id: str = ""
    title: str = ""
    detail: str = ""

class ResumeBase(BaseModel):
    title: str = "Frontend Developer Resume"
    template: str = "modern"
    targetRole: Optional[str] = ""
    atsScore: Optional[int] = 85
    personalInfo: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: str = ""
    education: List[EducationItem] = []
    experience: List[ExperienceItem] = []
    projects: List[ProjectItem] = []
    skills: SkillsData = Field(default_factory=SkillsData)
    certifications: List[CertificationItem] = []
    achievements: List[AchievementItem] = []
    tags: List[str] = []

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    template: Optional[str] = None
    targetRole: Optional[str] = None
    atsScore: Optional[int] = None
    personalInfo: Optional[PersonalInfo] = None
    summary: Optional[str] = None
    education: Optional[List[EducationItem]] = None
    experience: Optional[List[ExperienceItem]] = None
    projects: Optional[List[ProjectItem]] = None
    skills: Optional[SkillsData] = None
    certifications: Optional[List[CertificationItem]] = None
    achievements: Optional[List[AchievementItem]] = None
    tags: Optional[List[str]] = None

class ResumeResponse(ResumeBase):
    id: str
    updatedAt: str = "Just now"

    class Config:
        from_attributes = True

class UploadedFileResponse(BaseModel):
    id: str
    name: str
    size: str
    type: str
    uploadedAt: str
    status: str
    extractedText: Optional[str] = None
    parsedData: Optional[Dict[str, Any]] = None
