from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    # Resume can be provided by ID or raw data
    resumeId: Optional[str] = None
    uploadedFileId: Optional[str] = None
    resumeData: Optional[Dict[str, Any]] = None
    resumeText: Optional[str] = None

    # Job can be provided by ID or raw text or URL
    jobId: Optional[str] = None
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    jobText: Optional[str] = None
    jobUrl: Optional[str] = None

class SkillGapItem(BaseModel):
    skill: str
    status: str  # 'Strong' | 'Good' | 'Missing' | 'Partial'
    score: int
    category: str
    description: str

class LearningResource(BaseModel):
    title: str
    type: str
    provider: str
    duration: str
    link: str

class LearningRecommendation(BaseModel):
    id: str
    skill: str
    subtitle: str
    difficulty: str
    estimatedTime: str
    summary: str
    keyTopics: List[str]
    resources: List[LearningResource]

class ATSItem(BaseModel):
    id: str
    label: str
    passed: bool
    note: str

class ATSBreakdown(BaseModel):
    score: int
    verdict: str
    items: List[ATSItem]

class AnalysisResponse(BaseModel):
    jobTitle: str
    company: str
    matchScore: int
    atsScore: int
    status: str
    summary: str
    matchedSkills: List[str]
    missingSkills: List[str]
    partialSkills: List[str]
    skillGaps: List[SkillGapItem]
    learningRecommendations: List[LearningRecommendation]
    atsBreakdown: ATSBreakdown

class DashboardStatsResponse(BaseModel):
    totalAnalyses: int
    averageMatchScore: int
    topMissingSkill: str
    latestMatchScore: int
    totalSavedResumes: int
