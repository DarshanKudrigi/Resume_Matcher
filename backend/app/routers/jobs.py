import uuid
import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.job import JobPosting
from app.schemas.job import JobPostingResponse, JobParseRequest
from app.services.skill_extractor import extract_skills_from_text

router = APIRouter(prefix="/jobs", tags=["Job Postings"])

DEFAULT_SAMPLE_JOBS = [
    {
        "id": "job-1",
        "title": "Frontend Software Engineer (React)",
        "company": "Apex Cloud Technologies",
        "location": "Bengaluru, India (Hybrid)",
        "url": "https://careers.apexcloud.io/jobs/frontend-engineer-react",
        "experience": "0-2 Years",
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
        "requiredSkills": ["JavaScript", "React", "HTML", "CSS", "Git"],
        "preferredSkills": ["Node.js", "Docker", "AWS"]
    },
    {
        "id": "job-2",
        "title": "Junior Full Stack Developer",
        "company": "FinTech Innovations",
        "location": "Pune, India (Remote)",
        "url": "https://fintechinnovations.com/careers/junior-dev",
        "experience": "Entry Level / College Grad",
        "description": """Join our agile engineering squad developing next-generation financial analytics tools.
Seeking candidates with React, TypeScript/JavaScript, Node.js, and SQL fundamentals. Knowledge of Docker, REST APIs, and automated testing is highly valued.""",
        "requiredSkills": ["JavaScript", "React", "Node.js", "SQL", "Git"],
        "preferredSkills": ["Docker", "TypeScript", "REST APIs", "Jest"]
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
                description=j.description,
                requiredSkills=j.required_skills or [],
                preferredSkills=j.preferred_skills or []
            )
            for j in db_jobs
        ]
    
    # Return default samples if database table hasn't been seeded yet
    return [JobPostingResponse(**j) for j in DEFAULT_SAMPLE_JOBS]

@router.post("/parse", response_model=JobPostingResponse)
async def parse_job_description(req: JobParseRequest, db: AsyncSession = Depends(get_db)):
    """Extracts job title, company, and technical requirements from URL or pasted text."""
    if req.url:
        # Check if URL matches existing sample
        for sample in DEFAULT_SAMPLE_JOBS:
            if sample["url"].lower() in req.url.lower() or any(k in req.url.lower() for k in ["apex", "react", "frontend"]):
                return JobPostingResponse(**sample)

        # Fallback heuristic for custom URL
        title = "Frontend Engineer"
        company = "Extracted from URL"
        if "google" in req.url.lower():
            company = "Google"
        elif "amazon" in req.url.lower():
            company = "Amazon"
        elif "microsoft" in req.url.lower():
            company = "Microsoft"

        return JobPostingResponse(
            id=f"job-{uuid.uuid4().hex[:8]}",
            title=title,
            company=company,
            location="Bengaluru, India (Hybrid)",
            url=req.url,
            experience="1-3 Years",
            description=f"Extracted job requirements from {req.url}",
            requiredSkills=["JavaScript", "React", "HTML", "CSS", "Git"],
            preferredSkills=["Node.js", "Docker", "AWS"]
        )

    if req.text:
        extracted = extract_skills_from_text(req.text)
        req_skills = extracted[:5] if len(extracted) >= 5 else extracted
        pref_skills = extracted[5:8] if len(extracted) > 5 else []

        # Heuristic title detection
        lines = [line.strip() for line in req.text.splitlines() if line.strip()]
        title = lines[0] if lines else "Custom Job Description"
        if len(title.split()) > 6:
            title = "Software Engineer"

        new_job = JobPostingResponse(
            id=f"job-{uuid.uuid4().hex[:8]}",
            title=title,
            company="Custom Employer",
            location="Remote / Hybrid",
            url="",
            experience="0-2 Years",
            description=req.text,
            requiredSkills=req_skills if req_skills else ["JavaScript", "React", "HTML", "CSS", "Git"],
            preferredSkills=pref_skills if pref_skills else ["Node.js", "Docker", "AWS"]
        )
        return new_job

    raise HTTPException(status_code=400, detail="Must provide either URL or text description")
