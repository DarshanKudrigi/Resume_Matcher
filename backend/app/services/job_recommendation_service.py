import os
import sys
import csv
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, AsyncGenerator

# Ensure job-application-agent and its dependencies are in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
AGENT_DIR = BASE_DIR.parent / "job-application-agent"
AGENT_SITE_PACKAGES = AGENT_DIR / "venv" / "Lib" / "site-packages"

if AGENT_SITE_PACKAGES.exists() and str(AGENT_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(AGENT_SITE_PACKAGES))
if AGENT_DIR.exists() and str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

logger = logging.getLogger("resumemate.recommendations")

from app.schemas.recommendation import (
    JobRecommendationRequest,
    RecommendedJobItem,
    JobRecommendationResponse
)
from app.services.matcher_service import analyze_resume_against_job
from app.services.recommendations import get_recommendations_for_skills
from app.services.skill_extractor import extract_skills_from_text

TRACKED_CSV_PATH = BASE_DIR / "data" / "tracked_jobs.csv"
TRACKED_HEADERS = [
    "ID", "Title", "Company", "Location", "URL",
    "Source", "Match Score", "Recommendation",
    "Matched Skills", "Missing Skills", "Status", "Scraped At"
]

def log_to_local_csv(jobs_data: List[Dict[str, Any]]) -> int:
    """
    Appends jobs to a persistent local CSV tracker file, avoiding duplicate URLs or IDs.
    Returns the count of newly logged jobs.
    """
    TRACKED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing_ids = set()
    existing_urls = set()

    if TRACKED_CSV_PATH.exists():
        try:
            with open(TRACKED_CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if row:
                        if len(row) > 0 and row[0]:
                            existing_ids.add(row[0].strip())
                        if len(row) > 4 and row[4]:
                            clean_u = row[4].strip().split("?")[0].rstrip("/").lower()
                            existing_urls.add(clean_u)
        except Exception as e:
            logger.warning(f"Error reading existing tracked_jobs.csv: {e}")

    file_exists = TRACKED_CSV_PATH.exists() and TRACKED_CSV_PATH.stat().st_size > 0
    newly_added = 0

    try:
        with open(TRACKED_CSV_PATH, mode="a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(TRACKED_HEADERS)

            for j in jobs_data:
                jid = j.get("id", "")
                url = j.get("url", "")
                clean_url = url.strip().split("?")[0].rstrip("/").lower()

                if jid in existing_ids or (clean_url and clean_url in existing_urls):
                    continue

                score_pct = f"{j.get('matchScore', 0)}%"
                matched_str = ", ".join(j.get("matchedSkills", []))
                missing_str = ", ".join(j.get("missingSkills", []))

                writer.writerow([
                    jid,
                    j.get("title", ""),
                    j.get("company", ""),
                    j.get("location", ""),
                    url,
                    j.get("source", ""),
                    score_pct,
                    j.get("status", ""),
                    matched_str,
                    missing_str,
                    "Recommended",
                    j.get("scraped_at", datetime.now().isoformat())
                ])
                existing_ids.add(jid)
                if clean_url:
                    existing_urls.add(clean_url)
                newly_added += 1
    except Exception as e:
        logger.error(f"Failed to log jobs to local CSV: {e}")

    return newly_added


def log_to_google_sheets(agent_jobs: list) -> Tuple[bool, str]:
    """Attempts to log jobs to Google Sheets via existing sheets_tracker with socket timeout."""
    import socket
    prev_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(2.5)
        from tracker.sheets_tracker import log_jobs
        log_jobs(agent_jobs)
        return True, "Synced to Google Sheets & local tracker"
    except Exception as e:
        logger.info(f"Google Sheets sync not active or offline: {e}")
        return False, "Logged to local tracker (Google Sheets offline/sandboxed)"
    finally:
        socket.setdefaulttimeout(prev_timeout)


def _run_scraper_sync(platform: str, role: str, location: str, limit: int) -> Tuple[list, Optional[str]]:
    """Synchronous worker to run Playwright scraping in worker thread."""
    jobs = []
    error_msg = None
    try:
        if platform == "linkedin":
            from scraper.linkedin_scraper import LinkedInScraper
            scraper = LinkedInScraper(keywords=[role], location=location, headless=True)
            jobs = scraper.scrape(max_jobs=limit)
        elif platform == "naukri":
            from scraper.naukri_scraper import NaukriScraper
            scraper = NaukriScraper(keywords=[role], location=location, headless=True)
            jobs = scraper.scrape(max_jobs=limit)
        else:
            error_msg = f"Unknown platform: {platform}"
    except Exception as e:
        error_msg = f"{platform.capitalize()} notice: {str(e)}"
        logger.warning(error_msg)

    return jobs, error_msg


class JobRecommendationService:
    @staticmethod
    async def get_recommendations(req: JobRecommendationRequest) -> JobRecommendationResponse:
        role = req.desired_role.strip()
        loc = req.location.strip()
        platforms = [p.lower().strip() for p in req.platforms]
        limit_per_plat = max(1, min(req.limit, 10))

        warnings: List[str] = []
        all_raw_jobs = []

        for plat in platforms:
            if plat not in ["linkedin", "naukri"]:
                continue
            raw_jobs, err = await asyncio.to_thread(
                _run_scraper_sync, plat, role, loc, limit_per_plat
            )
            if err:
                warnings.append(err)
            if raw_jobs:
                all_raw_jobs.extend(raw_jobs)
            elif not err:
                warnings.append(f"{plat.capitalize()} returned 0 listings for '{role}' in '{loc}'.")

        resume_data = req.resume_data or {}
        resume_text = req.resume_text or ""

        recommended_items: List[RecommendedJobItem] = []
        agent_jobs_for_tracking = []

        for job in all_raw_jobs:
            try:
                meta = getattr(job, "match_meta", {}) or {}
                job_dict = {
                    "id": getattr(job, "id", ""),
                    "title": getattr(job, "title", "Role"),
                    "company": getattr(job, "company", "Company"),
                    "location": getattr(job, "location", loc),
                    "url": getattr(job, "url", ""),
                    "description": getattr(job, "description", ""),
                    "source": getattr(job, "source", "web"),
                    "scraped_at": getattr(job, "scraped_at", datetime.now().isoformat()),
                    "salary": meta.get("salary", "Not disclosed"),
                    "experience": meta.get("experience", "Not specified"),
                    "posted_date": meta.get("posted_date", "")
                }

                analysis = analyze_resume_against_job(
                    resume_data=resume_data,
                    job_data=job_dict,
                    resume_raw_text=resume_text
                )

                recs = get_recommendations_for_skills(getattr(analysis, "missingSkills", []), max_count=4)
                formatted_recs = []
                for r in recs:
                    r_dict = r.dict() if hasattr(r, "dict") else r
                    first_link = ""
                    source_name = ""
                    if r_dict.get("resources") and len(r_dict["resources"]) > 0:
                        first_link = r_dict["resources"][0].get("link", "")
                        source_name = r_dict["resources"][0].get("title", "")
                    formatted_recs.append({
                        "skill": r_dict.get("skill", ""),
                        "subtitle": r_dict.get("subtitle", ""),
                        "docUrl": first_link,
                        "sourceName": source_name,
                        "resources": r_dict.get("resources", [])
                    })

                rec_item = RecommendedJobItem(
                    id=job_dict["id"],
                    title=job_dict["title"],
                    company=job_dict["company"],
                    location=job_dict["location"],
                    url=job_dict["url"],
                    source=job_dict["source"],
                    scraped_at=job_dict["scraped_at"],
                    matchScore=getattr(analysis, "matchScore", 0),
                    status=getattr(analysis, "status", "Good Match"),
                    matchedSkills=getattr(analysis, "matchedSkills", []),
                    missingSkills=getattr(analysis, "missingSkills", []),
                    matchedPreferredSkills=getattr(analysis, "matchedPreferredSkills", []),
                    missingPreferredSkills=getattr(analysis, "missingPreferredSkills", []),
                    learningRecommendations=formatted_recs,
                    summary=getattr(analysis, "summary", ""),
                    description=job_dict["description"],
                    salary=job_dict["salary"],
                    experience=job_dict["experience"],
                    posted_date=job_dict["posted_date"]
                )
                recommended_items.append(rec_item)

                if hasattr(job, "match_score"):
                    job.match_score = getattr(analysis, "matchScore", 0) / 100.0
                    job.scored = True
                    job.match_meta.update({
                        "recommendation": getattr(analysis, "status", ""),
                        "matched_skills": getattr(analysis, "matchedSkills", []),
                        "missing_skills": getattr(analysis, "missingSkills", []),
                    })
                    agent_jobs_for_tracking.append(job)
            except Exception as item_err:
                logger.warning(f"Failed to analyze recommendation item: {item_err}")
                continue

        recommended_items.sort(key=lambda x: x.matchScore, reverse=True)

        jobs_dict_list = [item.dict() for item in recommended_items]
        new_local = log_to_local_csv(jobs_dict_list)

        sheets_ok, sheet_msg = False, "Saved to local tracker"
        if agent_jobs_for_tracking:
            sheets_ok, sheet_msg = await asyncio.to_thread(log_to_google_sheets, agent_jobs_for_tracking)

        final_spreadsheet_status = (
            f"Synced {len(recommended_items)} jobs to Google Sheets & local CSV"
            if sheets_ok else
            f"Logged {new_local} new job(s) to local tracker (tracked_jobs.csv)"
        )

        return JobRecommendationResponse(
            desired_role=role,
            location=loc,
            total_found=len(recommended_items),
            platforms_searched=platforms,
            warnings=warnings,
            spreadsheet_status=final_spreadsheet_status,
            jobs=recommended_items
        )

    @staticmethod
    async def stream_recommendations(req: JobRecommendationRequest) -> AsyncGenerator[str, None]:
        """
        Streams real-time execution progress events and the final results payload
        via Server-Sent Events (SSE), ensuring complete transparency across all 6 steps.
        """
        def format_event(payload: dict) -> str:
            return f"data: {json.dumps(payload)}\n\n"

        role = req.desired_role.strip()
        loc = req.location.strip()
        limit_per_plat = max(1, min(req.limit, 10))
        platforms = [p.lower().strip() for p in req.platforms]

        warnings: List[str] = []
        linkedin_jobs = []
        naukri_jobs = []
        recommended_items: List[RecommendedJobItem] = []

        try:
            # =========================================================================
            # STEP 1: RESUME PROCESSING
            # =========================================================================
            yield format_event({
                "step": 1,
                "type": "resume",
                "status": "processing",
                "message": "Validating candidate resume and extracting competencies..."
            })
            await asyncio.sleep(0.3)

            resume_data = req.resume_data or {}
            resume_text = req.resume_text or ""
            extracted_skills = []

            if resume_text:
                extracted_skills = extract_skills_from_text(resume_text)
            elif resume_data.get("extracted_skills"):
                extracted_skills = resume_data.get("extracted_skills")
            elif resume_data.get("skills"):
                s_obj = resume_data.get("skills")
                if isinstance(s_obj, dict):
                    for v in s_obj.values():
                        if isinstance(v, list):
                            extracted_skills.extend(v)

            skill_count = len(extracted_skills)
            yield format_event({
                "step": 1,
                "type": "resume",
                "status": "completed",
                "message": "Resume processed successfully.",
                "data": {
                    "skills_count": skill_count,
                    "top_skills": extracted_skills[:6]
                }
            })
            await asyncio.sleep(0.2)

            # =========================================================================
            # STEP 2: LINKEDIN JOB SEARCH (Up to 10)
            # =========================================================================
            if "linkedin" in platforms:
                yield format_event({
                    "step": 2,
                    "type": "linkedin",
                    "status": "processing",
                    "message": f"Searching LinkedIn for relevant {role} jobs in {loc}..."
                })

                raw_li, err_li = await asyncio.to_thread(
                    _run_scraper_sync, "linkedin", role, loc, limit_per_plat
                )

                if err_li:
                    warnings.append(err_li)
                    yield format_event({
                        "step": 2,
                        "type": "linkedin",
                        "status": "error",
                        "message": f"LinkedIn notice: {err_li}. Continuing with Naukri...",
                        "count": 0
                    })
                else:
                    linkedin_jobs = raw_li
                    yield format_event({
                        "step": 2,
                        "type": "linkedin",
                        "status": "completed",
                        "message": f"LinkedIn search completed! Found {len(linkedin_jobs)} jobs.",
                        "count": len(linkedin_jobs)
                    })
            else:
                yield format_event({
                    "step": 2,
                    "type": "linkedin",
                    "status": "completed",
                    "message": "LinkedIn search skipped (not selected).",
                    "count": 0
                })

            await asyncio.sleep(0.2)

            # =========================================================================
            # STEP 3: NAUKRI JOB SEARCH (Up to 10)
            # =========================================================================
            if "naukri" in platforms:
                yield format_event({
                    "step": 3,
                    "type": "naukri",
                    "status": "processing",
                    "message": "LinkedIn search completed. Now searching Naukri..."
                })

                raw_nk, err_nk = await asyncio.to_thread(
                    _run_scraper_sync, "naukri", role, loc, limit_per_plat
                )

                if err_nk:
                    warnings.append(err_nk)
                    yield format_event({
                        "step": 3,
                        "type": "naukri",
                        "status": "error",
                        "message": f"Naukri notice: {err_nk}.",
                        "count": 0
                    })
                else:
                    naukri_jobs = raw_nk
                    yield format_event({
                        "step": 3,
                        "type": "naukri",
                        "status": "completed",
                        "message": f"Naukri search completed! Found {len(naukri_jobs)} jobs.",
                        "count": len(naukri_jobs)
                    })
            else:
                yield format_event({
                    "step": 3,
                    "type": "naukri",
                    "status": "completed",
                    "message": "Naukri search skipped (not selected).",
                    "count": 0
                })

            await asyncio.sleep(0.2)

            # =========================================================================
            # STEP 4: JOB DETAILS EXTRACTION
            # =========================================================================
            all_raw_jobs = linkedin_jobs + naukri_jobs
            yield format_event({
                "step": 4,
                "type": "details",
                "status": "processing",
                "message": "Extracting job descriptions and required skills..."
            })
            await asyncio.sleep(0.3)

            yield format_event({
                "step": 4,
                "type": "details",
                "status": "completed",
                "message": f"Extracted descriptions & qualifications for {len(all_raw_jobs)} listings."
            })
            await asyncio.sleep(0.2)

            # =========================================================================
            # STEP 5: AI JOB MATCHING
            # =========================================================================
            yield format_event({
                "step": 5,
                "type": "matching",
                "status": "processing",
                "message": "Analyzing skills and calculating job match scores..."
            })

            agent_jobs_for_tracking = []

            for job in all_raw_jobs:
                try:
                    meta = getattr(job, "match_meta", {}) or {}
                    job_dict = {
                        "id": getattr(job, "id", ""),
                        "title": getattr(job, "title", "Role"),
                        "company": getattr(job, "company", "Company"),
                        "location": getattr(job, "location", loc),
                        "url": getattr(job, "url", ""),
                        "description": getattr(job, "description", ""),
                        "source": getattr(job, "source", "web"),
                        "scraped_at": getattr(job, "scraped_at", datetime.now().isoformat()),
                        "salary": meta.get("salary", "Not disclosed"),
                        "experience": meta.get("experience", "Not specified"),
                        "posted_date": meta.get("posted_date", "")
                    }

                    analysis = analyze_resume_against_job(
                        resume_data=resume_data,
                        job_data=job_dict,
                        resume_raw_text=resume_text
                    )

                    recs = get_recommendations_for_skills(getattr(analysis, "missingSkills", []), max_count=4)
                    formatted_recs = []
                    for r in recs:
                        r_dict = r.dict() if hasattr(r, "dict") else r
                        first_link = ""
                        source_name = ""
                        if r_dict.get("resources") and len(r_dict["resources"]) > 0:
                            first_link = r_dict["resources"][0].get("link", "")
                            source_name = r_dict["resources"][0].get("title", "")
                        formatted_recs.append({
                            "skill": r_dict.get("skill", ""),
                            "subtitle": r_dict.get("subtitle", ""),
                            "docUrl": first_link,
                            "sourceName": source_name,
                            "resources": r_dict.get("resources", [])
                        })

                    rec_item = RecommendedJobItem(
                        id=job_dict["id"],
                        title=job_dict["title"],
                        company=job_dict["company"],
                        location=job_dict["location"],
                        url=job_dict["url"],
                        source=job_dict["source"],
                        scraped_at=job_dict["scraped_at"],
                        matchScore=getattr(analysis, "matchScore", 0),
                        status=getattr(analysis, "status", "Good Match"),
                        matchedSkills=getattr(analysis, "matchedSkills", []),
                        missingSkills=getattr(analysis, "missingSkills", []),
                        matchedPreferredSkills=getattr(analysis, "matchedPreferredSkills", []),
                        missingPreferredSkills=getattr(analysis, "missingPreferredSkills", []),
                        learningRecommendations=formatted_recs,
                        summary=getattr(analysis, "summary", ""),
                        description=job_dict["description"],
                        salary=job_dict["salary"],
                        experience=job_dict["experience"],
                        posted_date=job_dict["posted_date"]
                    )
                    recommended_items.append(rec_item)

                    if hasattr(job, "match_score"):
                        job.match_score = getattr(analysis, "matchScore", 0) / 100.0
                        job.scored = True
                        job.match_meta.update({
                            "recommendation": getattr(analysis, "status", ""),
                            "matched_skills": getattr(analysis, "matchedSkills", []),
                            "missing_skills": getattr(analysis, "missingSkills", []),
                        })
                        agent_jobs_for_tracking.append(job)
                except Exception as item_err:
                    logger.warning(f"Error matching job {getattr(job, 'title', 'unknown')}: {item_err}")
                    continue

            recommended_items.sort(key=lambda x: x.matchScore, reverse=True)

            # Dual Logging: local CSV + Google Sheets (if accessible)
            jobs_dict_list = [item.dict() for item in recommended_items]
            new_local = log_to_local_csv(jobs_dict_list)

            sheets_ok, sheet_msg = False, "Saved to local tracker"
            if agent_jobs_for_tracking:
                sheets_ok, sheet_msg = await asyncio.to_thread(log_to_google_sheets, agent_jobs_for_tracking)

            final_spreadsheet_status = (
                f"Synced {len(recommended_items)} jobs to Google Sheets & local CSV"
                if sheets_ok else
                f"Logged {new_local} new job(s) to local tracker (tracked_jobs.csv)"
            )

            yield format_event({
                "step": 5,
                "type": "matching",
                "status": "completed",
                "message": "AI matching and official documentation roadmaps completed."
            })
            await asyncio.sleep(0.2)

            # =========================================================================
            # STEP 6: SEARCH COMPLETED
            # =========================================================================
            if recommended_items:
                comp_msg = f"Job search completed successfully! Found {len(recommended_items)} opportunities."
            elif warnings:
                comp_msg = f"Search completed: {'; '.join(warnings)}"
            else:
                comp_msg = f"Search completed. No active job openings were found for {role} in {loc}."

            yield format_event({
                "step": 6,
                "type": "complete",
                "status": "completed",
                "message": comp_msg,
                "data": {
                    "total_found": len(recommended_items),
                    "linkedin_count": len(linkedin_jobs),
                    "naukri_count": len(naukri_jobs),
                    "spreadsheet_status": final_spreadsheet_status,
                    "warnings": warnings,
                    "jobs": [item.dict() for item in recommended_items]
                }
            })

        except Exception as e:
            logger.error(f"Fatal error in stream_recommendations: {e}", exc_info=True)
            yield format_event({
                "step": 6,
                "type": "complete",
                "status": "error",
                "message": f"Search encountered an unexpected error: {str(e)}",
                "data": {
                    "total_found": len(recommended_items),
                    "linkedin_count": len(linkedin_jobs),
                    "naukri_count": len(naukri_jobs),
                    "spreadsheet_status": "Aborted due to error",
                    "warnings": warnings + [str(e)],
                    "jobs": [item.dict() for item in recommended_items]
                }
            })
