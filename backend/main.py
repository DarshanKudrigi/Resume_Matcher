import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import settings
from app.database import setup_database, Base, get_sessionmaker, ACTIVE_DB_TYPE
from app.models.user import User, Notification
from app.models.job import JobPosting
from app.models.resume import Resume
from app.models.history import AnalysisHistory
from app.services.auth_service import hash_password
from app.routers import (
    auth_router,
    users_router,
    resumes_router,
    jobs_router,
    analyze_router,
    history_router,
    dashboard_router,
    chat_router
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("resumemate")

async def seed_initial_data():
    """Seeds default sample user, jobs, and resumes if database is empty."""
    session_maker = get_sessionmaker()
    if not session_maker:
        return
    
    async with session_maker() as session:
        try:
            # Seed default user: Darshan Sharma
            result = await session.execute(select(User).where(User.email == "darshan.sharma@college.edu"))
            user = result.scalars().first()
            if not user:
                logger.info("Seeding initial user: darshan.sharma@college.edu...")
                user = User(
                    email="darshan.sharma@college.edu",
                    hashed_password=hash_password("password123"),
                    name="Darshan Sharma",
                    phone="+91 98765 43210",
                    location="Mumbai, India",
                    headline="Aspiring Frontend Engineer & CS Undergraduate",
                    avatar="DS",
                    linkedin="linkedin.com/in/darshansharma",
                    github="github.com/darshan-cs",
                    portfolio="darshansharma.dev",
                    college="National Institute of Technology",
                    degree="B.Tech in Computer Science and Engineering",
                    graduation_year="2026"
                )
                session.add(user)
                await session.flush()

                # Add sample notifications
                session.add_all([
                    Notification(
                        user_id=user.id,
                        title="Analysis Complete",
                        message="Your resume match score for Apex Cloud is 82%.",
                        time="10m ago",
                        unread=True
                    ),
                    Notification(
                        user_id=user.id,
                        title="ATS Tip",
                        message="Adding 'Docker' can increase your score by up to 8%.",
                        time="2h ago",
                        unread=True
                    ),
                    Notification(
                        user_id=user.id,
                        title="Resume Saved",
                        message="Frontend Developer Resume was updated.",
                        time="1d ago",
                        unread=False
                    )
                ])

            # Seed default sample jobs
            job_check = await session.execute(select(JobPosting).limit(1))
            if not job_check.scalars().first():
                logger.info("Seeding initial job postings...")
                from app.routers.jobs import DEFAULT_SAMPLE_JOBS
                for j in DEFAULT_SAMPLE_JOBS:
                    session.add(JobPosting(
                        id=j["id"],
                        title=j["title"],
                        company=j["company"],
                        location=j.get("location", ""),
                        url=j.get("url", ""),
                        experience=j.get("experience", ""),
                        description=j["description"],
                        required_skills=j["requiredSkills"],
                        preferred_skills=j["preferredSkills"]
                    ))

            # Seed default resume
            resume_check = await session.execute(select(Resume).limit(1))
            if not resume_check.scalars().first():
                logger.info("Seeding initial sample resume...")
                session.add(Resume(
                    id="resume-1",
                    user_id=user.id if user else None,
                    title="Frontend Developer Resume",
                    template="modern",
                    target_role="Frontend Software Engineer",
                    ats_score=86,
                    personal_info={
                        "fullName": "Darshan Sharma",
                        "email": "darshan.sharma@college.edu",
                        "phone": "+91 98765 43210",
                        "location": "Mumbai, India",
                        "linkedin": "linkedin.com/in/darshansharma",
                        "github": "github.com/darshan-cs",
                        "portfolio": "darshansharma.dev",
                        "headline": "Frontend React Developer & Final Year CS Student"
                    },
                    summary="Driven Computer Science undergraduate with practical experience in crafting responsive, user-centric web applications using React, JavaScript (ES6+), and modern CSS frameworks. Adept at building modular component architectures, optimizing client-side performance, and collaborating via Git version control.",
                    education=[
                        {
                            "id": "edu-1",
                            "institution": "National Institute of Technology",
                            "degree": "B.Tech in Computer Science & Engineering",
                            "location": "Mumbai, India",
                            "startDate": "Aug 2022",
                            "endDate": "Expected May 2026",
                            "score": "CGPA: 8.8 / 10.0"
                        }
                    ],
                    experience=[
                        {
                            "id": "exp-1",
                            "role": "Frontend Engineering Intern",
                            "company": "InnovateTech Solutions",
                            "location": "Remote",
                            "startDate": "May 2025",
                            "endDate": "Jul 2025",
                            "bullets": [
                                "Engineered 12+ responsive React components for customer analytics dashboard, reducing render times by 22%.",
                                "Integrated REST APIs with stateful custom hooks and implemented client-side form validation."
                            ]
                        }
                    ],
                    projects=[
                        {
                            "id": "proj-1",
                            "name": "ResumeMate - AI Resume & Job Matcher",
                            "tech": "React, Tailwind CSS, JavaScript, Context API",
                            "link": "https://github.com/darshan-cs/resume-mate",
                            "bullets": [
                                "Developed a modern client-side matching tool analyzing resumes against job descriptions.",
                                "Constructed an interactive live-preview resume builder supporting multiple modular themes."
                            ]
                        }
                    ],
                    skills={
                        "languages": ["JavaScript (ES6+)", "HTML5", "CSS3/Tailwind", "Python (Basics)", "SQL"],
                        "frameworks": ["React.js", "React Router", "Vite", "Node.js (Express Basics)"],
                        "tools": ["Git", "GitHub", "VS Code", "Postman", "Figma (Inspect)"],
                        "concepts": ["Component Architecture", "RESTful APIs", "Responsive Web Design", "Data Structures"]
                    },
                    certifications=[
                        {
                            "id": "cert-1",
                            "name": "Meta Front-End Developer Professional Certificate",
                            "issuer": "Coursera",
                            "year": "2025"
                        }
                    ],
                    achievements=[
                        {
                            "id": "ach-1",
                            "title": "1st Runner-Up, Inter-College Hackathon 2025",
                            "detail": "Built an accessibility-focused browser extension among 60+ participating teams."
                        }
                    ],
                    tags=["React", "JavaScript", "Tailwind CSS"]
                ))

            await session.commit()
            logger.info("Database seeding successfully completed!")
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await session.rollback()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: setup database engine and create tables
    logger.info("Starting up ResumeMate FastAPI backend...")
    db_engine = await setup_database()
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully.")
    
    # Seed initial test data
    await seed_initial_data()
    
    yield
    # Shutdown
    logger.info("Shutting down ResumeMate FastAPI backend...")
    if db_engine:
        await db_engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="High-performance backend for ResumeMate with PostgreSQL, Async SQLAlchemy, and AI Resume Matching.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(resumes_router, prefix=settings.API_PREFIX)
app.include_router(jobs_router, prefix=settings.API_PREFIX)
app.include_router(analyze_router, prefix=settings.API_PREFIX)
app.include_router(history_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "apiPrefix": settings.API_PREFIX,
        "status": "healthy"
    }

@app.get("/api/health")
async def health_check():
    from app.database import ACTIVE_DB_TYPE
    return {
        "status": "ok",
        "database": ACTIVE_DB_TYPE,
        "geminiEnabled": bool(settings.GEMINI_API_KEY)
    }
