from typing import List, Optional
from pydantic import BaseModel, Field

class SkillItem(BaseModel):
    name: str
    evidence: Optional[str] = ""
    category: Optional[str] = "Technical Skill"

class JobPostingBase(BaseModel):
    title: str = ""
    company: str = ""
    location: Optional[str] = ""
    url: Optional[str] = ""
    source_url: Optional[str] = ""
    experience: Optional[str] = ""
    experience_requirements: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    employment_type: Optional[str] = None
    employmentType: Optional[str] = None
    description: str = ""
    description_summary: Optional[str] = ""
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    
    # Structured skill items with evidence & category
    required_skills: List[SkillItem] = Field(default_factory=list)
    preferred_skills: List[SkillItem] = Field(default_factory=list)
    additional_mentioned_skills: List[SkillItem] = Field(default_factory=list)
    
    # Backward-compatible string name lists
    requiredSkills: List[str] = Field(default_factory=list)
    preferredSkills: List[str] = Field(default_factory=list)
    unclassifiedSkills: List[str] = Field(default_factory=list)

    source: Optional[str] = ""
    source_platform: Optional[str] = ""
    status: str = "success"  # "success" | "partial" | "error"
    extraction_status: str = "success"
    
    # Preserved original extracted text for verification
    raw_extracted_text: Optional[str] = ""
    
    unavailableFields: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errorMessage: Optional[str] = None

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingResponse(JobPostingBase):
    id: str

    class Config:
        from_attributes = True

class JobParseRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
