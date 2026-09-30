import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.resume import Resume, UploadedFile
from app.models.user import User
from app.schemas.resume import (
    ResumeCreate, ResumeUpdate, ResumeResponse, UploadedFileResponse
)
from app.services.auth_service import get_optional_current_user
from app.services.parser_service import (
    extract_text_from_pdf, extract_text_from_docx, parse_resume_content
)

router = APIRouter(prefix="/resumes", tags=["Resumes"])

def format_resume_response(res: Resume) -> ResumeResponse:
    return ResumeResponse(
        id=res.id,
        title=res.title,
        template=res.template or "modern",
        targetRole=res.target_role or "",
        atsScore=res.ats_score or 85,
        personalInfo=res.personal_info or {},
        summary=res.summary or "",
        education=res.education or [],
        experience=res.experience or [],
        projects=res.projects or [],
        skills=res.skills or {},
        certifications=res.certifications or [],
        achievements=res.achievements or [],
        tags=res.tags or [],
        updatedAt="Today" if (datetime.utcnow() - res.updated_at).days == 0 else f"{(datetime.utcnow() - res.updated_at).days}d ago"
    )

@router.get("", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all saved resumes for the user or public samples."""
    query = select(Resume).order_by(desc(Resume.updated_at))
    if current_user:
        query = query.where((Resume.user_id == current_user.id) | (Resume.user_id == None))
    
    result = await db.execute(query)
    resumes = result.scalars().all()
    return [format_resume_response(r) for r in resumes]

@router.post("", response_model=ResumeResponse)
async def create_resume(
    req: ResumeCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new resume in the builder."""
    new_res = Resume(
        id=f"res-{int(datetime.utcnow().timestamp())}",
        user_id=current_user.id if current_user else None,
        title=req.title,
        template=req.template,
        target_role=req.targetRole or "",
        ats_score=req.atsScore or 85,
        personal_info=req.personalInfo.model_dump(),
        summary=req.summary,
        education=[e.model_dump() for e in req.education],
        experience=[e.model_dump() for e in req.experience],
        projects=[p.model_dump() for p in req.projects],
        skills=req.skills.model_dump(),
        certifications=[c.model_dump() for c in req.certifications],
        achievements=[a.model_dump() for a in req.achievements],
        tags=req.tags
    )
    db.add(new_res)
    await db.commit()
    await db.refresh(new_res)
    return format_resume_response(new_res)

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves a single resume by ID."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return format_resume_response(resume)

@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: str,
    req: ResumeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Updates an existing resume."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if req.title is not None:
        resume.title = req.title
    if req.template is not None:
        resume.template = req.template
    if req.targetRole is not None:
        resume.target_role = req.targetRole
    if req.atsScore is not None:
        resume.ats_score = req.atsScore
    if req.personalInfo is not None:
        resume.personal_info = req.personalInfo.model_dump()
    if req.summary is not None:
        resume.summary = req.summary
    if req.education is not None:
        resume.education = [e.model_dump() for e in req.education]
    if req.experience is not None:
        resume.experience = [e.model_dump() for e in req.experience]
    if req.projects is not None:
        resume.projects = [p.model_dump() for p in req.projects]
    if req.skills is not None:
        resume.skills = req.skills.model_dump()
    if req.certifications is not None:
        resume.certifications = [c.model_dump() for c in req.certifications]
    if req.achievements is not None:
        resume.achievements = [a.model_dump() for a in req.achievements]
    if req.tags is not None:
        resume.tags = req.tags

    resume.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(resume)
    return format_resume_response(resume)

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deletes a saved resume."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    await db.delete(resume)
    await db.commit()
    return {"status": "deleted", "id": resume_id}

@router.post("/{resume_id}/duplicate", response_model=ResumeResponse)
async def duplicate_resume(
    resume_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clones an existing resume."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    source = result.scalars().first()
    if not source:
        raise HTTPException(status_code=404, detail="Source resume not found")

    duplicated = Resume(
        id=f"res-{int(datetime.utcnow().timestamp())}",
        user_id=current_user.id if current_user else source.user_id,
        title=f"{source.title} (Copy)",
        template=source.template,
        target_role=source.target_role,
        ats_score=source.ats_score,
        personal_info=source.personal_info,
        summary=source.summary,
        education=source.education,
        experience=source.experience,
        projects=source.projects,
        skills=source.skills,
        certifications=source.certifications,
        achievements=source.achievements,
        tags=source.tags
    )
    db.add(duplicated)
    await db.commit()
    await db.refresh(duplicated)
    return format_resume_response(duplicated)

@router.post("/upload", response_model=UploadedFileResponse)
async def upload_resume_file(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Uploads a PDF/DOCX resume file and parses its contents."""
    filename = file.filename or "resume.pdf"
    content = await file.read()
    size_mb = f"{len(content) / (1024 * 1024):.1f} MB"
    content_type = file.content_type or "application/pdf"

    # Extract text based on file format
    extracted_text = ""
    if filename.lower().endswith(".pdf") or "pdf" in content_type:
        try:
            extracted_text = extract_text_from_pdf(content)
        except Exception as e:
            extracted_text = f"Error reading PDF: {e}"
    elif filename.lower().endswith((".docx", ".doc")):
        try:
            extracted_text = extract_text_from_docx(content)
        except Exception as e:
            extracted_text = f"Error reading DOCX: {e}"
    else:
        try:
            extracted_text = content.decode("utf-8", errors="ignore")
        except Exception:
            extracted_text = ""

    parsed_data = parse_resume_content(extracted_text, filename)

    record = UploadedFile(
        id=f"file-{uuid.uuid4().hex[:8]}",
        user_id=current_user.id if current_user else None,
        filename=filename,
        file_size=size_mb,
        content_type=content_type,
        status="ready",
        extracted_text=extracted_text,
        parsed_data=parsed_data
    )
    db.add(record)
    await db.commit()

    return UploadedFileResponse(
        id=record.id,
        name=record.filename,
        size=record.file_size,
        type=record.content_type,
        uploadedAt="Just now",
        status="ready",
        extractedText=extracted_text,
        parsedData=parsed_data
    )
