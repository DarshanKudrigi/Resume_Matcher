import os
import sys
import json
import time
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, AsyncGenerator

# Ensure current directory is in sys.path
AGENT_ROOT = Path(__file__).resolve().parent
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from config import MATCH_THRESHOLD, AUTO_APPLY_THRESHOLD, GROQ_REQUEST_DELAY
from tracker.models import Job
from scraper.linkedin_scraper import LinkedInScraper
from scraper.naukri_scraper import NaukriScraper
from matcher.resume_matcher import score_job, filter_jobs

logger = logging.getLogger("job_application_agent.service")

def _safe_log_to_sheets(jobs: List[Job]) -> Tuple[bool, str]:
    """Safe wrapper for sheets_tracker.log_jobs with socket timeout."""
    try:
        import socket
        prev_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(3.0)
        try:
            from tracker.sheets_tracker import log_jobs
            log_jobs(jobs, min_threshold=MATCH_THRESHOLD)
            return True, "Synced to Google Sheets"
        finally:
            socket.setdefaulttimeout(prev_timeout)
    except Exception as e:
        logger.info(f"Google Sheets sync notice: {e}")
        return False, f"Google Sheets notice: {str(e)}"

def _run_scraper_sync(platform: str, role: str, location: str, max_jobs: int) -> Tuple[List[Job], Optional[str]]:
    """Synchronously executes the Job Application Agent scrapers."""
    jobs: List[Job] = []
    err: Optional[str] = None
    try:
        if platform == "linkedin":
            scraper = LinkedInScraper(keywords=[role], location=location, headless=True)
            jobs = scraper.scrape(max_jobs=max_jobs)
        elif platform == "naukri":
            scraper = NaukriScraper(keywords=[role], location=location, headless=True)
            jobs = scraper.scrape(max_jobs=max_jobs)
        else:
            err = f"Unknown platform: {platform}"
    except Exception as e:
        err = f"{platform.capitalize()} error: {str(e)}"
        logger.warning(err)
    return jobs, err

def _format_job_dict(job: Job) -> Dict[str, Any]:
    """Formats Job instance into a rich serializable dictionary for the frontend."""
    meta = job.match_meta or {}
    match_score_float = job.match_score if job.match_score is not None else 0.0
    match_percentage = int(match_score_float * 100) if match_score_float <= 1.0 else int(match_score_float)

    rec = meta.get("recommendation", "maybe" if match_percentage >= 50 else "skip")
    if rec == "apply":
        status_label = "Strong Match"
    elif rec == "maybe":
        status_label = "Good Match" if match_percentage >= 65 else "Moderate Match"
    else:
        status_label = "Low Match"

    matched_skills = meta.get("matched_skills", [])
    missing_skills = meta.get("missing_skills", [])

    return {
        "id": getattr(job, "id", ""),
        "title": getattr(job, "title", "Job Opening"),
        "company": getattr(job, "company", "Company"),
        "location": getattr(job, "location", ""),
        "url": getattr(job, "url", ""),
        "description": getattr(job, "description", ""),
        "source": getattr(job, "source", "linkedin"),
        "scraped_at": getattr(job, "scraped_at", datetime.now().isoformat()),
        "match_score": match_score_float,
        "matchScore": match_percentage,
        "status": status_label,
        "recommendation": rec,
        "reason": meta.get("reason") or (f"Scoring notice: {job.scoring_error}" if getattr(job, "scoring_error", None) else f"Groq score: {match_percentage}% match."),
        "experience_required": meta.get("experience_required", 0),
        "experience": meta.get("experience", "Not specified"),
        "salary": meta.get("salary", "Not disclosed"),
        "posted_date": meta.get("posted_date", ""),
        "matchedSkills": matched_skills,
        "missingSkills": missing_skills,
        "matchedPreferredSkills": matched_skills[3:] if len(matched_skills) > 3 else [],
        "missingPreferredSkills": missing_skills[3:] if len(missing_skills) > 3 else [],
    }

async def stream_agent_job_discovery(
    resume_text: str,
    desired_role: str = "Software Engineer",
    location: str = "Bangalore, Karnataka",
    limit_per_portal: int = 10,
    platforms: Optional[List[str]] = None
) -> AsyncGenerator[str, None]:
    """
    Executes the Job Application Agent workflow with transparent real-time Server-Sent Events (SSE)
    covering all 9 distinct steps:
      Step 1: Resume received.
      Step 2: LinkedIn search started.
      Step 3: LinkedIn search completed — X jobs found.
      Step 4: Naukri search started.
      Step 5: Naukri search completed — X jobs found.
      Step 6: Groq AI matching started.
      Step 7: Job results processed.
      Step 8: Google Sheets updated, if enabled.
      Step 9: Search completed.
    """
    def format_event(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    role = (desired_role or "Software Engineer").strip()
    loc = (location or "Bangalore, Karnataka").strip()
    limit = max(1, min(limit_per_portal or 10, 10))
    selected_platforms = [p.lower().strip() for p in (platforms or ["linkedin", "naukri"])]

    warnings: List[str] = []
    linkedin_jobs: List[Job] = []
    naukri_jobs: List[Job] = []
    all_jobs: List[Job] = []
    mod = sys.modules[__name__]

    try:
        # =========================================================================
        # STEP 1: RESUME RECEIVED
        # =========================================================================
        word_count = len(resume_text.split()) if resume_text else 0
        yield format_event({
            "step": 1,
            "type": "resume",
            "status": "completed",
            "message": f"Resume received successfully ({word_count} words parsed)." if word_count > 0 else "Resume context initialized.",
            "data": {"word_count": word_count}
        })
        await asyncio.sleep(0.2)

        # =========================================================================
        # STEP 2 & 3: LINKEDIN SEARCH
        # =========================================================================
        if "linkedin" in selected_platforms:
            yield format_event({
                "step": 2,
                "type": "linkedin_start",
                "status": "processing",
                "message": f"LinkedIn search started for '{role}' in '{loc}' (fetching up to {limit} jobs)..."
            })

            raw_li, err_li = await asyncio.to_thread(mod._run_scraper_sync, "linkedin", role, loc, limit)
            if err_li:
                warnings.append(err_li)
                yield format_event({
                    "step": 3,
                    "type": "linkedin_complete",
                    "status": "warning",
                    "message": f"LinkedIn notice: {err_li}",
                    "count": 0
                })
            else:
                linkedin_jobs = raw_li
                yield format_event({
                    "step": 3,
                    "type": "linkedin_complete",
                    "status": "completed",
                    "message": f"LinkedIn search completed — {len(linkedin_jobs)} jobs found.",
                    "count": len(linkedin_jobs)
                })
        else:
            yield format_event({
                "step": 3,
                "type": "linkedin_complete",
                "status": "completed",
                "message": "LinkedIn search skipped.",
                "count": 0
            })

        await asyncio.sleep(0.2)

        # =========================================================================
        # STEP 4 & 5: NAUKRI SEARCH
        # =========================================================================
        if "naukri" in selected_platforms:
            yield format_event({
                "step": 4,
                "type": "naukri_start",
                "status": "processing",
                "message": f"Naukri search started for '{role}' in '{loc}' (fetching up to {limit} jobs)..."
            })

            raw_nk, err_nk = await asyncio.to_thread(mod._run_scraper_sync, "naukri", role, loc, limit)
            if err_nk:
                warnings.append(err_nk)
                yield format_event({
                    "step": 5,
                    "type": "naukri_complete",
                    "status": "warning",
                    "message": f"Naukri notice: {err_nk}",
                    "count": 0
                })
            else:
                naukri_jobs = raw_nk
                yield format_event({
                    "step": 5,
                    "type": "naukri_complete",
                    "status": "completed",
                    "message": f"Naukri search completed — {len(naukri_jobs)} jobs found.",
                    "count": len(naukri_jobs)
                })
        else:
            yield format_event({
                "step": 5,
                "type": "naukri_complete",
                "status": "completed",
                "message": "Naukri search skipped.",
                "count": 0
            })

        await asyncio.sleep(0.2)

        # =========================================================================
        # STEP 6: GROQ AI MATCHING STARTED
        # =========================================================================
        all_jobs = linkedin_jobs + naukri_jobs
        total_to_score = len(all_jobs)

        yield format_event({
            "step": 6,
            "type": "matching_start",
            "status": "processing",
            "message": f"Groq AI matching started for {total_to_score} retrieved opportunities against your resume..."
        })
        await asyncio.sleep(0.2)

        scored_jobs: List[Job] = []
        for i, job in enumerate(all_jobs):
            try:
                # Score using the existing Groq AI matcher (handles cache & retries)
                scored = await asyncio.to_thread(mod.score_job, job, resume_text)
                scored_jobs.append(scored)
            except Exception as score_err:
                logger.warning(f"Error scoring job {job.title}: {score_err}")
                job.match_score = 0.5
                job.match_meta = {
                    "matched_skills": [],
                    "missing_skills": [],
                    "recommendation": "maybe",
                    "reason": f"Scoring notice: {str(score_err)}"
                }
                job.scored = True
                job.scoring_error = str(score_err)
                scored_jobs.append(job)

            # Sequential pacing delay between requests to prevent 429 rate limit spikes
            if i < len(all_jobs) - 1:
                await asyncio.sleep(GROQ_REQUEST_DELAY)

        # =========================================================================
        # STEP 7: JOB RESULTS PROCESSED
        # =========================================================================
        formatted_results = [_format_job_dict(j) for j in scored_jobs]
        formatted_results.sort(key=lambda x: x["matchScore"], reverse=True)

        yield format_event({
            "step": 7,
            "type": "processing_complete",
            "status": "completed",
            "message": f"Job results processed — scored and ranked {len(formatted_results)} opportunities.",
            "count": len(formatted_results)
        })
        await asyncio.sleep(0.2)

        # =========================================================================
        # STEP 8: GOOGLE SHEETS UPDATED
        # =========================================================================
        yield format_event({
            "step": 8,
            "type": "sheets_start",
            "status": "processing",
            "message": "Updating Google Sheets tracker with qualifying opportunities..."
        })

        sheets_ok, sheets_msg = await asyncio.to_thread(mod._safe_log_to_sheets, scored_jobs)
        yield format_event({
            "step": 8,
            "type": "sheets_complete",
            "status": "completed" if sheets_ok else "warning",
            "message": sheets_msg
        })
        await asyncio.sleep(0.2)

        # =========================================================================
        # STEP 9: SEARCH COMPLETED
        # =========================================================================
        if formatted_results:
            final_msg = f"Search completed successfully! Found {len(formatted_results)} matching jobs."
        elif warnings:
            final_msg = f"Search completed: {'; '.join(warnings)}"
        else:
            final_msg = f"Search completed. No active job openings were found for '{role}' in '{loc}'."

        yield format_event({
            "step": 9,
            "type": "search_completed",
            "status": "completed",
            "message": final_msg,
            "data": {
                "total_found": len(formatted_results),
                "linkedin_count": len(linkedin_jobs),
                "naukri_count": len(naukri_jobs),
                "spreadsheet_status": sheets_msg,
                "warnings": warnings,
                "jobs": formatted_results
            }
        })

    except Exception as e:
        logger.error(f"Fatal error in stream_agent_job_discovery: {e}", exc_info=True)
        yield format_event({
            "step": 9,
            "type": "search_completed",
            "status": "error",
            "message": f"Search encountered an unexpected error: {str(e)}",
            "data": {
                "total_found": 0,
                "linkedin_count": len(linkedin_jobs),
                "naukri_count": len(naukri_jobs),
                "spreadsheet_status": "Aborted",
                "warnings": warnings + [str(e)],
                "jobs": []
            }
        })

async def search_agent_jobs(
    resume_text: str,
    desired_role: str = "Software Engineer",
    location: str = "Bangalore, Karnataka",
    limit_per_portal: int = 10,
    platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Synchronous single-shot interface that delegates to stream_agent_job_discovery."""
    last_data: Dict[str, Any] = {
        "desired_role": desired_role,
        "location": location,
        "total_found": 0,
        "platforms_searched": platforms or ["linkedin", "naukri"],
        "warnings": [],
        "spreadsheet_status": "",
        "jobs": []
    }

    async for raw in stream_agent_job_discovery(
        resume_text=resume_text,
        desired_role=desired_role,
        location=location,
        limit_per_portal=limit_per_portal,
        platforms=platforms
    ):
        if raw.startswith("data: "):
            payload = json.loads(raw[6:].strip())
            if payload.get("step") == 9 and payload.get("data"):
                d = payload["data"]
                last_data["total_found"] = d.get("total_found", 0)
                last_data["warnings"] = d.get("warnings", [])
                last_data["spreadsheet_status"] = d.get("spreadsheet_status", "")
                last_data["jobs"] = d.get("jobs", [])

    return last_data
