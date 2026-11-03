from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class JobRecommendationRequest(BaseModel):
    desired_role: str = Field(default="Software Engineer", description="Target job title or keywords, e.g. 'Software Engineer'")
    location: str = Field(default="Bangalore, Karnataka", description="Target location, e.g. 'Bangalore, Karnataka' or 'Remote'")
    platforms: List[str] = Field(default=["linkedin", "naukri"], description="Job boards to search")
    limit: int = Field(default=10, description="Max jobs to retrieve per platform (top 10)")
    resume_data: Optional[Dict[str, Any]] = Field(default=None, description="Active candidate resume structured data")
    resume_text: Optional[str] = Field(default=None, description="Raw extracted resume text")
    uploaded_file_id: Optional[str] = Field(default=None, description="Uploaded resume file ID if stored")

class RecommendedJobItem(BaseModel):
    id: str
    title: str
    company: str
    location: str
    url: str
    source: str
    scraped_at: str
    matchScore: int
    status: str
    matchedSkills: List[str] = []
    missingSkills: List[str] = []
    matchedPreferredSkills: List[str] = []
    missingPreferredSkills: List[str] = []
    learningRecommendations: List[Dict[str, Any]] = []
    summary: str = ""
    description: str = ""
    salary: Optional[str] = ""
    experience: Optional[str] = ""
    posted_date: Optional[str] = ""

class JobRecommendationResponse(BaseModel):
    desired_role: str
    location: str
    total_found: int
    platforms_searched: List[str]
    warnings: List[str] = []
    spreadsheet_status: str
    jobs: List[RecommendedJobItem] = []
