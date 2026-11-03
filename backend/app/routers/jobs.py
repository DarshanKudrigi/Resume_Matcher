import uuid
import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.job import JobPosting
from app.schemas.job import JobPostingResponse, JobParseRequest
from app.services.job_extraction import extract_and_process_job

router = APIRouter(prefix="/jobs", tags=["Job Postings"])

DEFAULT_SAMPLE_JOBS = [
    {
        "id": "job-1",
        "title": "Frontend Software Engineer (React)",
        "company": "Apex Cloud Technologies",
        "location": "Bengaluru, India (Hybrid)",
        "url": "https://careers.apexcloud.io/jobs/frontend-engineer-react",
        "experience": "0-2 Years",
        "employmentType": "Full-Time",
        "description": """We are looking for a passionate Frontend Software Engineer with a solid foundation in modern JavaScript, React, HTML, and CSS to join our core product team.

Responsibilities:
- Build responsive, accessible, and high-performance user interfaces using React and modern CSS.
- Collaborate with product designers and backend engineers to integrate RESTful APIs.
- Write modular, clean, and reusable component code using Git for version control.
- Participate in code reviews and contribute to developer documentation.

Requirements:
- Strong proficiency in JavaScript (ES6+), React hooks, HTML5, and CSS3.
- Hands-on experience with Git version control and collaborative workflows.
- Understanding of web performance, responsive layouts, and cross-browser quirks.
- Preferred familiarity with Node.js, Docker containers, and AWS cloud deployment environments.""",
        "responsibilities": [
            "Build responsive, accessible, and high-performance user interfaces using React and modern CSS.",
            "Collaborate with product designers and backend engineers to integrate RESTful APIs.",
            "Write modular, clean, and reusable component code using Git for version control.",
            "Participate in code reviews and contribute to developer documentation."
        ],
        "qualifications": [
            "Strong proficiency in JavaScript (ES6+), React hooks, HTML5, and CSS3.",
            "Hands-on experience with Git version control and collaborative workflows.",
            "Understanding of web performance, responsive layouts, and cross-browser quirks.",
            "Preferred familiarity with Node.js, Docker containers, and AWS cloud deployment environments."
        ],
        "requiredSkills": ["JavaScript", "React", "HTML", "CSS", "Git"],
        "preferredSkills": ["Node.js", "Docker", "AWS"],
        "unclassifiedSkills": [],
        "source": "Apex Cloud Careers",
        "status": "success",
        "unavailableFields": [],
        "warnings": []
    },
    {
        "id": "job-2",
        "title": "Junior Full Stack Developer",
        "company": "FinTech Innovations",
        "location": "Pune, India (Remote)",
        "url": "https://fintechinnovations.com/careers/junior-dev",
        "experience": "Entry Level / College Grad",
        "employmentType": "Full-Time",
        "description": """Join our agile engineering squad developing next-generation financial analytics tools.
Seeking candidates with React, TypeScript/JavaScript, Node.js, and SQL fundamentals. Knowledge of Docker, REST APIs, and automated testing is highly valued.""",
        "responsibilities": [
            "Develop next-generation financial analytics dashboards and tools.",
            "Write well-tested backend APIs and frontend modular components."
        ],
        "qualifications": [
            "React, TypeScript/JavaScript, Node.js, and SQL fundamentals.",
            "Knowledge of Docker, REST APIs, and automated testing is highly valued."
        ],
        "requiredSkills": ["JavaScript", "React", "Node.js", "SQL", "Git"],
        "preferredSkills": ["Docker", "TypeScript", "REST APIs", "Jest"],
        "unclassifiedSkills": [],
        "source": "FinTech Careers",
        "status": "success",
        "unavailableFields": [],
        "warnings": []
    }
]

@router.get("", response_model=List[JobPostingResponse])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    """Retrieves all available job postings."""
    result = await db.execute(select(JobPosting))
    db_jobs = result.scalars().all()
    if db_jobs:
        return [
            JobPostingResponse(
                id=j.id,
                title=j.title,
                company=j.company,
                location=j.location or "",
                url=j.url or "",
                experience=j.experience or "",
                employmentType=getattr(j, "employment_type", "") or "Full-Time",
                description=j.description,
                responsibilities=[],
                qualifications=[],
                requiredSkills=j.required_skills or [],
                preferredSkills=j.preferred_skills or [],
                unclassifiedSkills=[],
                source=getattr(j, "source", "") or "Database",
                status="success",
                unavailableFields=[],
                warnings=[]
            )
            for j in db_jobs
        ]
    
    # Return default samples if database table hasn't been seeded yet
    return [JobPostingResponse(**j) for j in DEFAULT_SAMPLE_JOBS]

@router.post("/parse", response_model=JobPostingResponse)
async def parse_job_description(req: JobParseRequest, db: AsyncSession = Depends(get_db)):
    """
    Extracts structured job posting details from a URL using hybrid extraction
    (Job Application Agent / Lightweight Extractor + Gemini AI),
    or parses raw pasted job description text.
    """
    if not req.url and not req.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either a job URL or job description text."
        )

    try:
        result = await extract_and_process_job(url=req.url, text=req.text)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job extraction error: {str(e)}"
        )

    # If extraction was blocked by third-party website (authentication/bot protection)
    # or failed, return the structured JobPostingResponse with status="error" and errorMessage
    # so the frontend can display the notice and let the user paste text, avoiding a false API 403.
    return result
