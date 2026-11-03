import asyncio
import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Add job-application-agent to sys.path so its modules can be reused cleanly
AGENT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "job-application-agent"
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from scraper.url_scraper import IndividualJobScraper, RawJobData
from app.config import settings
from app.schemas.job import JobPostingResponse
from app.services.skill_extractor import extract_skills_from_text

logger = logging.getLogger("resumemate.job_scraper")

# Singleton instance of IndividualJobScraper
_scraper_instance: Optional[IndividualJobScraper] = None

def get_url_scraper() -> IndividualJobScraper:
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = IndividualJobScraper(headless=True, timeout_ms=30000)
    return _scraper_instance

# Linguistic cue patterns for sentence-level classification
REQUIREMENT_CUES = re.compile(
    r'\b(?:must\s+have|required|requirement|minimum|essential|mandatory|strong\s+proficiency|proficiency\s+in|hands-on\s+experience\s+with|at\s+least|bachelor|\d+\+?\s+years?\s+of)\b',
    re.IGNORECASE
)
PREFERENCE_CUES = re.compile(
    r'\b(?:preferred|nice\s+to\s+have|plus|bonus|desirable|desired|optional|advantageous|familiarity\s+with|good\s+to\s+have)\b',
    re.IGNORECASE
)

def classify_skills_from_job(raw_job: RawJobData) -> Tuple[List[str], List[str], List[str]]:
    """
    Deterministically classifies skills into Required, Preferred, and Unclassified
    using section headers and sentence-level contextual cues.
    """
    req_skills: Set[str] = set()
    pref_skills: Set[str] = set()
    unclassified_skills: Set[str] = set()

    has_explicit_sections = bool(raw_job.basic_qualifications_text or raw_job.preferred_qualifications_text)

    # 1. Deterministic extraction from explicit sections if available
    if raw_job.basic_qualifications_text:
        extracted_req = extract_skills_from_text(raw_job.basic_qualifications_text)
        req_skills.update(extracted_req)

    if raw_job.preferred_qualifications_text:
        extracted_pref = extract_skills_from_text(raw_job.preferred_qualifications_text)
        pref_skills.update(extracted_pref)

    # Remove duplicates from preferred if already marked required
    pref_skills = pref_skills - req_skills

    # 2. If no explicit sections were found, or to catch skills in general description
    full_text = raw_job.description or ""
    all_jd_skills = extract_skills_from_text(full_text)

    if not has_explicit_sections:
        # Split text into sentences for sentence-level cue inspection
        sentences = re.split(r'[.\n;•]+', full_text)
        
        for skill in all_jd_skills:
            skill_lower = skill.lower()
            matched_required = False
            matched_preferred = False

            for sent in sentences:
                if re.search(r'\b' + re.escape(skill_lower) + r'\b', sent, re.IGNORECASE):
                    if REQUIREMENT_CUES.search(sent):
                        matched_required = True
                        break
                    elif PREFERENCE_CUES.search(sent):
                        matched_preferred = True

            if matched_required:
                req_skills.add(skill)
            elif matched_preferred:
                pref_skills.add(skill)
            else:
                unclassified_skills.add(skill)
    else:
        # Explicit sections exist. If there are other skills in description not in either section,
        # classify them as unclassified
        remaining = set(all_jd_skills) - req_skills - pref_skills
        unclassified_skills.update(remaining)

    # 3. Optional Groq-assisted refinement for unclassified skills if explicitly configured in backend settings
    groq_key = settings.GROQ_API_KEY
    if groq_key and unclassified_skills and len(unclassified_skills) <= 15:
        try:
            req_refined, pref_refined = _classify_with_groq(
                list(unclassified_skills), full_text[:4000], groq_key
            )
            req_skills.update(req_refined)
            pref_skills.update(pref_refined)
            unclassified_skills = unclassified_skills - set(req_refined) - set(pref_refined)
        except Exception as e:
            logger.warning(f"Groq skill classification skipped: {e}")

    return sorted(list(req_skills)), sorted(list(pref_skills)), sorted(list(unclassified_skills))

def _classify_with_groq(candidate_skills: List[str], jd_text: str, api_key: str) -> Tuple[List[str], List[str]]:
    """Strict non-hallucinating classification using Groq LLM with temperature=0 and 5s timeout."""
    try:
        from groq import Groq
        client = Groq(api_key=api_key, timeout=5.0)
    except Exception:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1", timeout=5.0)
        except Exception:
            return [], []

    prompt = f"""You are a strict technical recruiter. Given this Job Description and a list of candidate skills found in the text, classify each skill strictly based on whether the JD states it is a REQUIRED qualification or a PREFERRED (optional/nice-to-have) qualification.

RULES:
- ONLY classify skills from the CANDIDATE SKILLS list. Do NOT invent new skills.
- If a skill cannot be clearly established as required or preferred, omit it.
- Return ONLY valid JSON with shape:
{{"required": ["skill1"], "preferred": ["skill2"]}}

CANDIDATE SKILLS: {json.dumps(candidate_skills)}

JOB DESCRIPTION:
{jd_text}
"""
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL or "openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
            timeout=5.0
        )
        raw = response.choices[0].message.content or ""
        data = json.loads(raw)
        
        # Strictly validate against original candidates
        candidate_set = set(candidate_skills)
        req = [s for s in data.get("required", []) if s in candidate_set]
        pref = [s for s in data.get("preferred", []) if s in candidate_set and s not in req]
        return req, pref
    except Exception as e:
        logger.warning(f"Groq API call skipped or timed out: {e}")
        return [], []

async def scrape_and_parse_job(url: str) -> JobPostingResponse:
    """
    Orchestrates URL scraping in a background thread, skill extraction,
    and returns a normalized JobPostingResponse.
    """
    scraper = get_url_scraper()
    
    # Run Playwright scraping synchronously in a thread to keep FastAPI event loop unblocked
    raw_job: RawJobData = await asyncio.to_thread(scraper.scrape_url, url)

    # If scraping failed completely
    if raw_job.status == "error":
        return JobPostingResponse(
            id=f"err-{hashlib.md5(url.encode()).hexdigest()[:8]}",
            title="Extraction Failed",
            company="",
            location="",
            url=url,
            experience="",
            employmentType="",
            description="",
            responsibilities=[],
            qualifications=[],
            requiredSkills=[],
            preferredSkills=[],
            unclassifiedSkills=[],
            source=raw_job.source or "Web",
            status="error",
            unavailableFields=["title", "company", "description"],
            warnings=raw_job.warnings,
            errorMessage=raw_job.error_message or "Could not extract job posting from URL."
        )

    # Classify required and preferred skills
    req_skills, pref_skills, unclass_skills = classify_skills_from_job(raw_job)

    # Stable unique ID based on job_id or url hash
    clean_id = raw_job.job_id or hashlib.md5(url.encode()).hexdigest()[:10]
    unique_id = f"job-{clean_id}"

    # Responsibilities and Qualifications fallback
    responsibilities = raw_job.responsibilities
    qualifications = raw_job.qualifications

    # Determine status (success vs partial)
    final_status = "success"
    if raw_job.status == "partial" or not req_skills or not responsibilities:
        final_status = "partial"

    return JobPostingResponse(
        id=unique_id,
        title=raw_job.title or "Untitled Position",
        company=raw_job.company or "Unknown Company",
        location=raw_job.location or "",
        url=raw_job.url,
        experience=raw_job.experience or "",
        employmentType=raw_job.employment_type or "",
        description=raw_job.description,
        responsibilities=responsibilities,
        qualifications=qualifications,
        requiredSkills=req_skills,
        preferredSkills=pref_skills,
        unclassifiedSkills=unclass_skills,
        source=raw_job.source or "Web",
        status=final_status,
        unavailableFields=raw_job.unavailable_fields,
        warnings=raw_job.warnings,
        errorMessage=raw_job.error_message
    )
