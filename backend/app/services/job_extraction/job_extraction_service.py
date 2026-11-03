import asyncio
import hashlib
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add job-application-agent to sys.path
AGENT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "job-application-agent"
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from app.config import settings
from app.schemas.job import JobPostingResponse, SkillItem
from app.services.skill_extractor import extract_skills_from_text, get_skill_metadata
from .url_classifier import classify_job_url, URLCategory
from .lightweight_extractor import extract_job_content_lightweight, RawExtractedContent
from .gemini_service import (
    call_gemini_structured_extraction,
    GeminiStructuredOutput,
    GeminiConfigurationError,
    GeminiExtractionError
)

logger = logging.getLogger("resumemate.job_extraction_service")

# Lazy-loaded IndividualJobScraper instance from job-application-agent
_agent_scraper = None

def get_agent_scraper():
    global _agent_scraper
    if _agent_scraper is None:
        from scraper.url_scraper import IndividualJobScraper
        _agent_scraper = IndividualJobScraper(headless=True, timeout_ms=30000)
    return _agent_scraper

def _deterministic_skill_fallback(
    text: str,
    basic_quals_text: str = "",
    pref_quals_text: str = ""
) -> Tuple[List[SkillItem], List[SkillItem], List[SkillItem]]:
    """Deterministic skill extraction fallback when Gemini API is unavailable."""
    req_skills: List[SkillItem] = []
    pref_skills: List[SkillItem] = []
    add_skills: List[SkillItem] = []

    seen = set()

    if basic_quals_text:
        for s in extract_skills_from_text(basic_quals_text):
            if s.lower() not in seen:
                seen.add(s.lower())
                meta = get_skill_metadata(s)
                req_skills.append(SkillItem(name=s, evidence="Found in requirements", category=meta.get("category", "Technical Skill")))

    if pref_quals_text:
        for s in extract_skills_from_text(pref_quals_text):
            if s.lower() not in seen:
                seen.add(s.lower())
                meta = get_skill_metadata(s)
                pref_skills.append(SkillItem(name=s, evidence="Found in preferred qualifications", category=meta.get("category", "Technical Skill")))

    # All remaining skills in full text
    for s in extract_skills_from_text(text):
        if s.lower() not in seen:
            seen.add(s.lower())
            meta = get_skill_metadata(s)
            add_skills.append(SkillItem(name=s, evidence="Mentioned in job description", category=meta.get("category", "Technical Skill")))

    # If no explicit sections existed, split heuristics
    if not basic_quals_text and not pref_quals_text and add_skills:
        req_skills = add_skills[:5]
        pref_skills = add_skills[5:8] if len(add_skills) > 5 else []
        add_skills = add_skills[8:] if len(add_skills) > 8 else []

    return req_skills, pref_skills, add_skills

def _normalize_gemini_output(
    gemini_out: GeminiStructuredOutput,
    raw_text: str,
    url: str,
    platform: str,
    warnings: List[str]
) -> JobPostingResponse:
    """Converts GeminiStructuredOutput into full JobPostingResponse."""
    clean_id = hashlib.md5((url or raw_text[:100]).encode()).hexdigest()[:10]
    unique_id = f"job-{clean_id}"

    # Convert to SkillItem objects
    req_items = [
        SkillItem(name=s.get_name(), evidence=s.evidence or "", category=s.category or "Technical Skill")
        for s in gemini_out.required_skills if s.get_name()
    ]
    pref_items = [
        SkillItem(name=s.get_name(), evidence=s.evidence or "", category=s.category or "Technical Skill")
        for s in gemini_out.preferred_skills if s.get_name()
    ]
    add_items = [
        SkillItem(name=s.get_name(), evidence=s.evidence or "", category=s.category or "Technical Skill")
        for s in gemini_out.additional_mentioned_skills if s.get_name()
    ]

    exp_list = gemini_out.get_experience_list()
    edu_list = gemini_out.get_education_list()
    resp_list = gemini_out.get_responsibilities_list()
    qual_list = gemini_out.get_qualifications_list()

    unavailable: List[str] = []
    if not gemini_out.location:
        unavailable.append("location")
    if not exp_list:
        unavailable.append("experience")
    if not resp_list:
        unavailable.append("responsibilities")
    if not qual_list:
        unavailable.append("qualifications")

    status = "success"
    if not req_items and not pref_items:
        status = "partial"

    final_title = gemini_out.get_title() or "Untitled Position"

    return JobPostingResponse(
        id=unique_id,
        title=final_title,
        company=gemini_out.company or "Company not specified",
        location=gemini_out.location or "",
        url=url,
        source_url=url,
        experience=", ".join(exp_list) if exp_list else "",
        experience_requirements=exp_list,
        education_requirements=edu_list,
        employment_type=gemini_out.employment_type or "Full-Time",
        employmentType=gemini_out.employment_type or "Full-Time",
        description=raw_text,
        description_summary=gemini_out.description_summary or raw_text[:300],
        responsibilities=resp_list,
        qualifications=qual_list,
        required_skills=req_items,
        preferred_skills=pref_items,
        additional_mentioned_skills=add_items,
        requiredSkills=[s.name for s in req_items],
        preferredSkills=[s.name for s in pref_items],
        unclassifiedSkills=[s.name for s in add_items],
        source=platform,
        source_platform=platform,
        status=status,
        extraction_status=status,
        raw_extracted_text=raw_text,
        unavailableFields=unavailable,
        warnings=warnings
    )

async def extract_and_process_job(
    url: Optional[str] = None,
    text: Optional[str] = None
) -> JobPostingResponse:
    """
    Main entry point for hybrid job extraction:
    - LinkedIn & Naukri: Scraped via existing Job Application Agent -> passed to Gemini.
    - Other Websites: Extracted via lightweight HTTP (or Playwright) -> passed to Gemini.
    - Manual text: Passed directly to Gemini.
    - Fallback: Deterministic NLP extraction if GEMINI_API_KEY is not configured.
    """
    warnings: List[str] = []
    raw_text = ""
    job_title = ""
    company = ""
    location = ""
    platform = "Web"
    source_url = url or ""

    if url:
        category, platform_name, parsed_url = classify_job_url(url)
        platform = platform_name

        if category in (URLCategory.LINKEDIN, URLCategory.NAUKRI):
            # A. LinkedIn and Naukri URLs -> Use existing Job Application Agent
            logger.info(f"Routing {category.value} URL to Job Application Agent: {url}")
            agent = get_agent_scraper()
            raw_data = await asyncio.to_thread(agent.scrape_url, url)

            if raw_data.status == "error":
                return JobPostingResponse(
                    id=f"err-{hashlib.md5(url.encode()).hexdigest()[:8]}",
                    title="Extraction Blocked or Failed",
                    company="",
                    location="",
                    url=url,
                    source_url=url,
                    description="",
                    source=platform,
                    source_platform=platform,
                    status="error",
                    extraction_status="error",
                    errorMessage=(
                        f"{platform} requires authentication or restricted automated access: "
                        f"{raw_data.error_message or 'Page could not be extracted.'} "
                        "You can paste the job description text manually below."
                    ),
                    unavailableFields=["title", "company", "description"],
                    warnings=raw_data.warnings
                )

            raw_text = raw_data.description
            job_title = raw_data.title
            company = raw_data.company
            location = raw_data.location
            warnings.extend(raw_data.warnings)

        else:
            # B. All Other Job Websites -> Lightweight Extraction (HTTP -> Playwright)
            logger.info(f"Routing {platform} URL to Lightweight Extractor: {url}")
            lightweight_data: RawExtractedContent = await extract_job_content_lightweight(url, platform)

            if not lightweight_data.success:
                return JobPostingResponse(
                    id=f"err-{hashlib.md5(url.encode()).hexdigest()[:8]}",
                    title="Extraction Failed",
                    company="",
                    location="",
                    url=url,
                    source_url=url,
                    description="",
                    source=platform,
                    source_platform=platform,
                    status="error",
                    extraction_status="error",
                    errorMessage=(
                        f"{lightweight_data.error_message or 'Could not extract job posting.'} "
                        "You can paste the job description text manually below."
                    ),
                    unavailableFields=["title", "company", "description"],
                    warnings=lightweight_data.warnings
                )

            raw_text = lightweight_data.visible_text
            job_title = lightweight_data.title
            company = lightweight_data.company
            location = lightweight_data.location
            warnings.extend(lightweight_data.warnings)

    elif text:
        # User manually pasted the job description
        raw_text = text.strip()
        platform = "Manual Paste"
        source_url = ""
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        job_title = lines[0] if lines and len(lines[0].split()) <= 7 else "Custom Job Posting"
        company = "Employer"

    else:
        raise ValueError("Must provide either a job URL or job description text.")

    if not raw_text or len(raw_text.strip()) < 30:
        return JobPostingResponse(
            id=f"err-{hashlib.md5((source_url or 'empty').encode()).hexdigest()[:8]}",
            title="Insufficient Job Content",
            company="",
            location="",
            url=source_url,
            source_url=source_url,
            description=raw_text,
            source=platform,
            source_platform=platform,
            status="error",
            extraction_status="error",
            errorMessage="The extracted content was too short or empty. Please paste the job description manually.",
            unavailableFields=["description"]
        )

    # 3. Pass to Gemini API for clean structured extraction & classification
    has_gemini = bool((settings.GEMINI_API_KEY or "").strip())
    
    if has_gemini:
        try:
            logger.info("Passing extracted job content to Gemini API for structured classification...")
            meta_info = {"title": job_title, "company": company, "location": location, "platform": platform}
            gemini_out = await call_gemini_structured_extraction(raw_text, meta_info=meta_info)
            return _normalize_gemini_output(gemini_out, raw_text, source_url, platform, warnings)
        except GeminiConfigurationError as gce:
            warnings.append(str(gce))
        except GeminiExtractionError as gee:
            warnings.append(f"Gemini AI processing error: {str(gee)}. Fell back to deterministic NLP rules.")
            logger.warning(f"Gemini extraction failed: {gee}")
    else:
        warnings.append("GEMINI_API_KEY is not configured in backend/.env. Using built-in deterministic NLP rules.")

    # 4. Fallback: Deterministic skill extraction if Gemini is unconfigured or failed
    req_items, pref_items, add_items = _deterministic_skill_fallback(raw_text)

    clean_id = hashlib.md5((source_url or raw_text[:100]).encode()).hexdigest()[:10]
    unique_id = f"job-{clean_id}"

    return JobPostingResponse(
        id=unique_id,
        title=job_title or "Job Posting",
        company=company or "Company not specified",
        location=location or "",
        url=source_url,
        source_url=source_url,
        experience="Experience details not specified",
        experience_requirements=[],
        education_requirements=[],
        employment_type="Full-Time",
        employmentType="Full-Time",
        description=raw_text,
        description_summary=raw_text[:280] + ("..." if len(raw_text) > 280 else ""),
        responsibilities=[],
        qualifications=[],
        required_skills=req_items,
        preferred_skills=pref_items,
        additional_mentioned_skills=add_items,
        requiredSkills=[s.name for s in req_items],
        preferredSkills=[s.name for s in pref_items],
        unclassifiedSkills=[s.name for s in add_items],
        source=platform,
        source_platform=platform,
        status="partial" if has_gemini else "success",
        extraction_status="partial" if has_gemini else "success",
        raw_extracted_text=raw_text,
        unavailableFields=["responsibilities", "qualifications"],
        warnings=warnings
    )
