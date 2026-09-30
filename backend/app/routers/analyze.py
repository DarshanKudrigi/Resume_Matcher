import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.resume import Resume, UploadedFile
from app.models.job import JobPosting
from app.models.history import AnalysisHistory
from app.models.user import User
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.auth_service import get_optional_current_user
from app.services.matcher_service import analyze_resume_against_job
from app.routers.jobs import DEFAULT_SAMPLE_JOBS

router = APIRouter(prefix="/analyze", tags=["Resume Analysis Engine"])

@router.post("", response_model=AnalysisResponse)
async def analyze_resume(
    req: AnalysisRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Executes matching algorithm between resume and job description."""
    # 1. Resolve Resume Data
    resume_data = req.resumeData or {}
    resume_raw_text = req.resumeText or ""

    if req.resumeId and not resume_data:
        res = await db.execute(select(Resume).where(Resume.id == req.resumeId))
        found_resume = res.scalars().first()
        if found_resume:
            resume_data = {
                "title": found_resume.title,
                "personalInfo": found_resume.personal_info,
                "summary": found_resume.summary,
                "education": found_resume.education,
                "experience": found_resume.experience,
                "projects": found_resume.projects,
                "skills": found_resume.skills,
                "certifications": found_resume.certifications,
                "achievements": found_resume.achievements,
                "tags": found_resume.tags
            }

    if req.uploadedFileId and not resume_data:
        res = await db.execute(select(UploadedFile).where(UploadedFile.id == req.uploadedFileId))
        found_file = res.scalars().first()
        if found_file:
            resume_data = found_file.parsed_data or {}
            resume_raw_text = found_file.extracted_text or ""

    # Default fallback resume data if empty
    if not resume_data:
        resume_data = {
            "title": "Frontend Developer Resume",
            "personalInfo": {
                "fullName": "Darshan Sharma",
                "email": "darshan.sharma@college.edu",
                "phone": "+91 98765 43210",
                "linkedin": "linkedin.com/in/darshansharma",
                "github": "github.com/darshan-cs"
            },
            "summary": "Driven CS undergraduate skilled in React, JavaScript, HTML, CSS, and Git.",
            "skills": {
                "languages": ["JavaScript", "HTML", "CSS", "Python", "SQL"],
                "frameworks": ["React", "React Router", "Node.js"],
                "tools": ["Git", "GitHub", "VS Code"],
                "concepts": ["Component Architecture", "RESTful APIs"]
            },
            "projects": [
                {
                    "name": "ResumeMate - AI Resume & Job Matcher",
                    "tech": "React, Tailwind CSS, JavaScript"
                }
            ]
        }

    # 2. Resolve Job Data
    job_data = {}
    if req.jobId:
        res = await db.execute(select(JobPosting).where(JobPosting.id == req.jobId))
        found_job = res.scalars().first()
        if found_job:
            job_data = {
                "title": found_job.title,
                "company": found_job.company,
                "description": found_job.description,
                "requiredSkills": found_job.required_skills,
                "preferredSkills": found_job.preferred_skills
            }
        else:
            # Check default sample jobs
            matched_sample = next((j for j in DEFAULT_SAMPLE_JOBS if j["id"] == req.jobId), None)
            if matched_sample:
                job_data = matched_sample

    if not job_data:
        job_data = {
            "title": req.jobTitle or "Frontend Software Engineer (React)",
            "company": req.company or "Apex Cloud Technologies",
            "description": req.jobText or DEFAULT_SAMPLE_JOBS[0]["description"],
            "requiredSkills": ["JavaScript", "React", "HTML", "CSS", "Git"],
            "preferredSkills": ["Node.js", "Docker", "AWS"]
        }

    # 3. Perform analysis
    analysis_result = analyze_resume_against_job(resume_data, job_data, resume_raw_text)

    # 4. Save to history table in PostgreSQL
    history_record = AnalysisHistory(
        id=f"hist-{int(datetime.utcnow().timestamp())}",
        user_id=current_user.id if current_user else None,
        job_title=analysis_result.jobTitle,
        company=analysis_result.company,
        match_score=analysis_result.matchScore,
        ats_score=analysis_result.atsScore,
        status=analysis_result.status,
        missing_count=len(analysis_result.missingSkills),
        matched_count=len(analysis_result.matchedSkills),
        skills=analysis_result.matchedSkills,
        full_result=analysis_result.model_dump()
    )
    db.add(history_record)
    await db.commit()

    return analysis_result
