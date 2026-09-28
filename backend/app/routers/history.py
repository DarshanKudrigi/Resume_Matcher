from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.history import AnalysisHistory
from app.models.user import User
from app.schemas.analysis import HistoryItemResponse
from app.services.auth_service import get_optional_current_user

router = APIRouter(prefix="/history", tags=["Analysis History"])

DEFAULT_SAMPLE_HISTORY = [
    {
        "id": "hist-1",
        "jobTitle": "Frontend Developer",
        "company": "Apex Cloud Technologies",
        "matchScore": 82,
        "atsScore": 86,
        "date": "Today, 11:20 AM",
        "dateFormatted": "Today",
        "status": "Strong Match",
        "missingCount": 3,
        "matchedCount": 5,
        "skills": ["JavaScript", "React", "HTML", "CSS", "Git"]
    },
    {
        "id": "hist-2",
        "jobTitle": "Software Engineer",
        "company": "FinTech Global",
        "matchScore": 76,
        "atsScore": 80,
        "date": "Sep 18, 2026",
        "dateFormatted": "Sep 18",
        "status": "Good Match",
        "missingCount": 4,
        "matchedCount": 6,
        "skills": ["React", "JavaScript", "SQL", "Node.js"]
    },
    {
        "id": "hist-3",
        "jobTitle": "Data Analyst",
        "company": "DataScale AI",
        "matchScore": 71,
        "atsScore": 74,
        "date": "Sep 15, 2026",
        "dateFormatted": "Sep 15",
        "status": "Moderate Match",
        "missingCount": 5,
        "matchedCount": 4,
        "skills": ["Python", "SQL", "Git"]
    },
    {
        "id": "hist-4",
        "jobTitle": "React Developer Intern",
        "company": "NextGen Labs",
        "matchScore": 88,
        "atsScore": 91,
        "date": "Aug 29, 2026",
        "dateFormatted": "Aug 29",
        "status": "Excellent Match",
        "missingCount": 2,
        "matchedCount": 7,
        "skills": ["React", "JavaScript", "HTML", "CSS", "Git", "REST APIs"]
    }
]

def format_history_response(h: AnalysisHistory) -> HistoryItemResponse:
    date_str = h.created_at.strftime("%b %d, %Y")
    is_today = (datetime.utcnow().date() == h.created_at.date())
    formatted = "Today" if is_today else h.created_at.strftime("%b %d")

    return HistoryItemResponse(
        id=h.id,
        jobTitle=h.job_title,
        company=h.company,
        matchScore=h.match_score,
        atsScore=h.ats_score,
        date=f"{formatted}, {h.created_at.strftime('%I:%M %p')}",
        dateFormatted=formatted,
        status=h.status,
        missingCount=h.missing_count,
        matchedCount=h.matched_count,
        skills=h.skills or [],
        fullResult=h.full_result
    )

@router.get("", response_model=List[HistoryItemResponse])
async def get_history(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all past resume audit and match history."""
    query = select(AnalysisHistory).order_by(desc(AnalysisHistory.created_at))
    if current_user:
        query = query.where((AnalysisHistory.user_id == current_user.id) | (AnalysisHistory.user_id == None))
    
    result = await db.execute(query)
    records = result.scalars().all()

    if records:
        return [format_history_response(r) for r in records]

    # Return default initial history if no runs yet
    return [HistoryItemResponse(**h) for h in DEFAULT_SAMPLE_HISTORY]

@router.get("/{history_id}", response_model=HistoryItemResponse)
async def get_history_detail(
    history_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves details of a past analysis."""
    result = await db.execute(select(AnalysisHistory).where(AnalysisHistory.id == history_id))
    record = result.scalars().first()
    if not record:
        # Check sample history
        matched = next((h for h in DEFAULT_SAMPLE_HISTORY if h["id"] == history_id), None)
        if matched:
            return HistoryItemResponse(**matched)
        raise HTTPException(status_code=404, detail="History record not found")

    return format_history_response(record)

@router.delete("/{history_id}")
async def delete_history_item(
    history_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deletes an analysis history item."""
    result = await db.execute(select(AnalysisHistory).where(AnalysisHistory.id == history_id))
    record = result.scalars().first()
    if record:
        await db.delete(record)
        await db.commit()
    return {"status": "deleted", "id": history_id}
