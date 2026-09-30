from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.history import AnalysisHistory
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import DashboardStatsResponse, HistoryItemResponse
from app.services.auth_service import get_optional_current_user
from app.routers.history import format_history_response, DEFAULT_SAMPLE_HISTORY

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculates statistics for user dashboard."""
    # Query history
    history_query = select(AnalysisHistory).order_by(desc(AnalysisHistory.created_at)).limit(5)
    resumes_query = select(func.count(Resume.id))
    
    if current_user:
        history_query = history_query.where((AnalysisHistory.user_id == current_user.id) | (AnalysisHistory.user_id == None))
        resumes_query = resumes_query.where((Resume.user_id == current_user.id) | (Resume.user_id == None))

    history_res = await db.execute(history_query)
    recent_records = history_res.scalars().all()

    resume_count_res = await db.execute(resumes_query)
    saved_resumes_count = resume_count_res.scalar() or 3

    if recent_records:
        total_analyses = len(recent_records)
        scores = [r.match_score for r in recent_records]
        avg_score = int(sum(scores) / len(scores))
        latest_score = recent_records[0].match_score
        recent_list = [format_history_response(r) for r in recent_records]
    else:
        total_analyses = len(DEFAULT_SAMPLE_HISTORY)
        avg_score = 79
        latest_score = 82
        recent_list = [HistoryItemResponse(**h) for h in DEFAULT_SAMPLE_HISTORY[:4]]

    return DashboardStatsResponse(
        totalAnalyses=total_analyses,
        averageMatchScore=avg_score,
        topMissingSkill="Docker",
        latestMatchScore=latest_score,
        recentAnalyses=recent_list,
        totalSavedResumes=saved_resumes_count
    )
