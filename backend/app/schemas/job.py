from typing import List, Optional
from pydantic import BaseModel

class JobPostingBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = ""
    url: Optional[str] = ""
    experience: Optional[str] = ""
    description: str
    requiredSkills: List[str] = []
    preferredSkills: List[str] = []

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingResponse(JobPostingBase):
    id: str

    class Config:
        from_attributes = True

class JobParseRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
