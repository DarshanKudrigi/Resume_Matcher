from app.schemas.auth import (
    UserRegister, UserLogin, UserProfileUpdate, UserResponse, TokenResponse
)
from app.schemas.resume import (
    ResumeBase, ResumeCreate, ResumeUpdate, ResumeResponse, UploadedFileResponse,
    PersonalInfo, EducationItem, ExperienceItem, ProjectItem, SkillsData,
    CertificationItem, AchievementItem
)
from app.schemas.job import (
    JobPostingBase, JobPostingCreate, JobPostingResponse, JobParseRequest
)
from app.schemas.analysis import (
    AnalysisRequest, AnalysisResponse, SkillGapItem, LearningRecommendation,
    ATSBreakdown, ATSItem, DashboardStatsResponse
)
from app.schemas.chat import (
    ChatMessageRequest, ChatMessageResponse, AISuggestionsResponse
)

__all__ = [
    "UserRegister", "UserLogin", "UserProfileUpdate", "UserResponse", "TokenResponse",
    "ResumeBase", "ResumeCreate", "ResumeUpdate", "ResumeResponse", "UploadedFileResponse",
    "PersonalInfo", "EducationItem", "ExperienceItem", "ProjectItem", "SkillsData",
    "CertificationItem", "AchievementItem",
    "JobPostingBase", "JobPostingCreate", "JobPostingResponse", "JobParseRequest",
    "AnalysisRequest", "AnalysisResponse", "SkillGapItem", "LearningRecommendation",
    "ATSBreakdown", "ATSItem", "DashboardStatsResponse",
    "ChatMessageRequest", "ChatMessageResponse", "AISuggestionsResponse"
]
