import os
import re
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pypdf.errors import PdfReadError

from app.config import settings, BASE_DIR
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

UPLOAD_DIR = Path(BASE_DIR) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit

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
        id=f"res-{uuid.uuid4().hex[:8]}",
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
        id=f"res-{uuid.uuid4().hex[:8]}",
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
    """
    Uploads a resume PDF or document with validation, safe local file storage,
    multi-page text extraction, OCR fallback where necessary, section parsing,
    and database persistence.
    """
    raw_filename = file.filename or "resume.pdf"
    
    # 1. Sanitize filename to prevent path traversal
    base_name = os.path.basename(raw_filename)
    clean_filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', base_name)
    if not clean_filename or clean_filename.startswith('.'):
        clean_filename = f"resume_{uuid.uuid4().hex[:6]}.pdf"

    # 2. Read and validate file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}"
        )

    # Validate size: reject empty or oversized
    file_size_bytes = len(content)
    if file_size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes). Please upload a valid resume."
        )

    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        actual_mb = file_size_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size ({max_mb:.0f} MB). Uploaded size: {actual_mb:.1f} MB."
        )

    # 3. Validate file type and contents
    lower_name = clean_filename.lower()
    content_type = file.content_type or "application/octet-stream"

    is_pdf = lower_name.endswith(".pdf") or "pdf" in content_type
    is_docx = lower_name.endswith((".docx", ".doc")) or "word" in content_type
    is_txt = lower_name.endswith(".txt") or "text/plain" in content_type

    if not is_pdf and not is_docx and not is_txt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF (.pdf), Word (.docx), or plain text (.txt) document."
        )

    # Validate PDF Magic Bytes (%PDF-)
    if is_pdf:
        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF format: File header does not match a valid PDF structure (%PDF-)."
            )

    size_mb_str = f"{file_size_bytes / (1024 * 1024):.1f} MB"
    file_id = f"file-{uuid.uuid4().hex[:10]}"
    storage_filename = f"{file_id}_{clean_filename}"
    storage_path = UPLOAD_DIR / storage_filename

    # 4. Save file to controlled local storage
    try:
        with open(storage_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file to server storage: {str(e)}"
        )

    # 5. Extract text and handle errors / OCR
    extracted_text = ""
    page_count = 1
    ocr_applied = False
    status_msg = "ready"
    err_msg = None

    if is_pdf:
        try:
            extracted_text, page_count, ocr_applied, status_msg = extract_text_from_pdf(content)
        except ValueError as ve:
            # E.g., password-protected or encrypted PDF
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except PdfReadError as pre:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Corrupted or unreadable PDF: {str(pre)}"
            )
        except Exception as e:
            err_msg = f"Error extracting PDF: {str(e)}"
            status_msg = "error"
    elif is_docx:
        try:
            extracted_text = extract_text_from_docx(content)
            status_msg = "DOCX extraction successful."
        except Exception as e:
            err_msg = f"Error extracting DOCX: {str(e)}"
            status_msg = "error"
    elif is_txt:
        extracted_text = content.decode("utf-8", errors="ignore")
        status_msg = "Text extraction successful."

    # 6. Parse structured resume sections & NLP
    parsed_data = parse_resume_content(extracted_text, clean_filename)
    parsed_data["file_path"] = f"uploads/{storage_filename}"
    parsed_data["ocr_applied"] = ocr_applied
    parsed_data["page_count"] = page_count

    # 7. Persist in database
    file_record_status = "ready" if extracted_text.strip() else ("needs_ocr" if is_pdf else "empty")
    record = UploadedFile(
        id=file_id,
        user_id=current_user.id if current_user else None,
        filename=clean_filename,
        file_size=size_mb_str,
        content_type=content_type,
        status=file_record_status,
        file_path=f"uploads/{storage_filename}",
        extracted_text=extracted_text,
        parsed_data=parsed_data,
        created_at=datetime.utcnow()
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return UploadedFileResponse(
        id=record.id,
        name=record.filename,
        size=record.file_size,
        type=record.content_type,
        uploadedAt="Just now",
        status=record.status,
        extractedText=extracted_text,
        parsedData=parsed_data,
        filePath=record.file_path,
        errorMessage=err_msg,
        pageCount=page_count
    )

@router.get("/files/{file_id}", response_model=UploadedFileResponse)
async def get_uploaded_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves an uploaded resume file and its parsed sections by ID."""
    result = await db.execute(select(UploadedFile).where(UploadedFile.id == file_id))
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Uploaded file not found")
    
    return UploadedFileResponse(
        id=record.id,
        name=record.filename,
        size=record.file_size,
        type=record.content_type,
        uploadedAt=record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else "Earlier",
        status=record.status,
        extractedText=record.extracted_text,
        parsedData=record.parsed_data,
        filePath=record.file_path,
        pageCount=(record.parsed_data or {}).get("page_count", 1)
    )

@router.get("/files", response_model=List[UploadedFileResponse])
async def list_uploaded_files(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists recently uploaded resume files."""
    query = select(UploadedFile).order_by(desc(UploadedFile.created_at)).limit(20)
    if current_user:
        query = query.where((UploadedFile.user_id == current_user.id) | (UploadedFile.user_id == None))
    
    result = await db.execute(query)
    records = result.scalars().all()
    return [
        UploadedFileResponse(
            id=r.id,
            name=r.filename,
            size=r.file_size,
            type=r.content_type,
            uploadedAt=r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "Earlier",
            status=r.status,
            extractedText=r.extracted_text,
            parsedData=r.parsed_data,
            filePath=r.file_path,
            pageCount=(r.parsed_data or {}).get("page_count", 1)
        )
        for r in records
    ]
