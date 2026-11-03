import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.schemas.recommendation import JobRecommendationRequest, JobRecommendationResponse

# Ensure Job Application Agent is in sys.path as the sole authorized job-search engine
AGENT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "job-application-agent"
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from agent_service import stream_agent_job_discovery, search_agent_jobs

router = APIRouter(prefix="/recommendations", tags=["Job Recommendations (Job Application Agent)"])

def _extract_resume_text(req: JobRecommendationRequest) -> str:
    """Extracts dynamic resume text without writing or modifying files on disk."""
    if req.resume_text and req.resume_text.strip():
        return req.resume_text.strip()
    
    if req.resume_data:
        cand_skills = []
        skills = req.resume_data.get("skills", {})
        if isinstance(skills, dict):
            for v in skills.values():
                if isinstance(v, list):
                    cand_skills.extend(v)
        elif isinstance(skills, list):
            cand_skills.extend(skills)
        name = req.resume_data.get("personalInfo", {}).get("fullName", "Candidate")
        summary = req.resume_data.get("summary", "")
        return f"Candidate: {name}\nSummary: {summary}\nSkills: {', '.join(cand_skills)}"

    return ""

@router.post("/search", response_model=JobRecommendationResponse)
async def search_job_recommendations(req: JobRecommendationRequest):
    """
    Delegates job search directly to the Job Application Agent:
    LinkedIn Scraper + Naukri Scraper + Groq Matcher + Google Sheets Tracker.
    """
    if not req.desired_role.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Desired job role cannot be empty."
        )
    if not req.location.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preferred location cannot be empty."
        )

    resume_text = _extract_resume_text(req)
    try:
        data = await search_agent_jobs(
            resume_text=resume_text,
            desired_role=req.desired_role,
            location=req.location,
            limit_per_portal=req.limit or 10,
            platforms=req.platforms
        )
        return JobRecommendationResponse(**data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job Application Agent failed: {str(e)}"
        )

@router.post("/stream")
async def stream_job_recommendations(req: JobRecommendationRequest):
    """
    Streams live progress directly from the Job Application Agent across 9 steps:
    1. Resume received.
    2. LinkedIn search started.
    3. LinkedIn search completed — X jobs found.
    4. Naukri search started.
    5. Naukri search completed — X jobs found.
    6. Groq AI matching started.
    7. Job results processed.
    8. Google Sheets updated, if enabled.
    9. Search completed.
    """
    if not req.desired_role.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Desired job role cannot be empty."
        )
    if not req.location.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preferred location cannot be empty."
        )

    resume_text = _extract_resume_text(req)

    return StreamingResponse(
        stream_agent_job_discovery(
            resume_text=resume_text,
            desired_role=req.desired_role,
            location=req.location,
            limit_per_portal=req.limit or 10,
            platforms=req.platforms
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
