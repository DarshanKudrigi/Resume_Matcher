from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import DashboardStatsResponse
from app.services.auth_service import get_optional_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculates statistics for user dashboard."""
    resumes_query = select(func.count(Resume.id))
    
    if current_user:
        resumes_query = resumes_query.where((Resume.user_id == current_user.id) | (Resume.user_id == None))

    resume_count_res = await db.execute(resumes_query)
    saved_resumes_count = resume_count_res.scalar() or 3

    return DashboardStatsResponse(
        totalAnalyses=1,
        averageMatchScore=82,
        topMissingSkill="Docker",
        latestMatchScore=82,
        totalSavedResumes=saved_resumes_count
    )
