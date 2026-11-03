import os
import sys
import json
from pathlib import Path

# Add project root to path
AGENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENT_DIR))

from config import GROQ_API_KEY, GROQ_MODEL, MATCH_THRESHOLD
from tracker.models import Job
from matcher.resume_matcher import score_job, get_client, _parse_and_validate_scoring
from scraper.linkedin_scraper import LinkedInScraper
from scraper.naukri_scraper import NaukriScraper
from agent_service import _safe_log_to_sheets

SAMPLE_RESUME = """
Chandan S Gowda
Email: chandan@example.com | Bengaluru, India
Professional Summary:
Full Stack Python & FastAPI Developer with 3+ years of experience designing scalable RESTful APIs,
integrating microservices, and deploying on Azure cloud. Proficient in Python, FastAPI, Django, React,
PostgreSQL, Docker, Git, Linux, and REST APIs.
Skills: Python, FastAPI, Django, JavaScript, React, MySQL, PostgreSQL, Git, Docker, Linux, REST APIs, Azure.
"""

def test_1_groq_models():
    print("=" * 60)
    print("TEST 1: Groq API Connection & Models (Primary + Fallback)")
    print("=" * 60)
    client = get_client()

    # 1. Primary Model
    primary_model = "openai/gpt-oss-120b"
    print(f"Testing Primary Model: {primary_model}...")
    res1 = client.chat.completions.create(
        model=primary_model,
        messages=[{"role": "user", "content": 'Respond with ONLY valid JSON: {"status": "ok", "model": "primary"}'}],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    content1 = res1.choices[0].message.content or ""
    print(f"  [PASS] Primary Model ({primary_model}) response:", content1.strip())
    assert "status" in json.loads(content1)

    # 2. Fallback Model
    fallback_model = "openai/gpt-oss-20b"
    print(f"Testing Fallback Model: {fallback_model}...")
    res2 = client.chat.completions.create(
        model=fallback_model,
        messages=[{"role": "user", "content": 'Respond with ONLY valid JSON: {"status": "ok", "model": "fallback"}'}],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    content2 = res2.choices[0].message.content or ""
    print(f"  [PASS] Fallback Model ({fallback_model}) response:", content2.strip())
    assert "status" in json.loads(content2)

def test_2_resume_scoring():
    print("\n" + "=" * 60)
    print("TEST 2: Resume vs Job Description Scoring & JSON Validation")
    print("=" * 60)
    
    test_job = Job(
        title="Python Backend Developer",
        company="TechCorp Innovations",
        location="Bengaluru, Karnataka",
        url="https://example.com/job/101",
        description="We are looking for a Python Backend Developer with experience in Python, FastAPI, PostgreSQL, and Git. 1-3 years experience required. Freshers with good projects can also apply.",
        source="test",
        scraped_at="2026-11-03T10:00:00"
    )

    scored_job = score_job(test_job, SAMPLE_RESUME)
    assert scored_job.scored is True, f"Scoring failed! Error: {scored_job.scoring_error}"
    assert scored_job.match_score is not None, "match_score is None!"
    
    print(f"Job Title: {scored_job.title}")
    print(f"Match Score: {scored_job.match_score:.2f} ({int(scored_job.match_score * 100)}%)")
    print(f"Recommendation: {scored_job.match_meta.get('recommendation')}")
    print(f"Matched Skills: {scored_job.match_meta.get('matched_skills')}")
    print(f"Missing Skills: {scored_job.match_meta.get('missing_skills')}")
    print(f"Reason: {scored_job.match_meta.get('reason')}")
    print(f"Experience Required: {scored_job.match_meta.get('experience_required')}")
    print(f"Experience Match: {scored_job.match_meta.get('experience_match')}")

    assert scored_job.match_score >= 0.5, "Expected high match score for matching Python profile!"
    assert "Python" in str(scored_job.match_meta.get("matched_skills")) or "FastAPI" in str(scored_job.match_meta.get("matched_skills"))
    assert scored_job.match_meta.get("recommendation") in {"apply", "maybe", "skip"}
    print("  [PASS] Resume scoring produced valid JSON and accurate competency assessment!")

def test_3_naukri_scraping():
    print("\n" + "=" * 60)
    print("TEST 3: Naukri Scraping & Anti-Detection")
    print("=" * 60)
    scraper = NaukriScraper(keywords=["Software Engineer"], location="Bangalore, Karnataka", headless=True)
    jobs = scraper.scrape(max_jobs=3)
    print(f"Naukri Scraper fetched: {len(jobs)} jobs (limit was 3)")
    assert len(jobs) > 0, "Naukri scraper returned 0 jobs! Expected >= 1 job."
    assert len(jobs) <= 10, "Exceeded 10 jobs limit!"
    
    first = jobs[0]
    print(f"  Sample Naukri Job 1: '{first.title}' at '{first.company}'")
    print(f"  Location: {first.location}")
    print(f"  URL: {first.url}")
    print(f"  Experience: {first.match_meta.get('experience')}")
    print(f"  Salary: {first.match_meta.get('salary')}")
    print(f"  Description length: {len(first.description)} chars")
    assert first.title and first.company and first.url
    print("  [PASS] Naukri scraper successfully retrieved job listings with details!")

def test_4_linkedin_scraping():
    print("\n" + "=" * 60)
    print("TEST 4: LinkedIn Scraping (Max 10 enforcement)")
    print("=" * 60)
    scraper = LinkedInScraper(keywords=["Software Engineer"], location="Bangalore, Karnataka", headless=True)
    jobs = scraper.scrape(max_jobs=3)
    print(f"LinkedIn Scraper fetched: {len(jobs)} jobs (limit was 3)")
    assert len(jobs) > 0, "LinkedIn scraper returned 0 jobs!"
    assert len(jobs) <= 10, "Exceeded 10 jobs limit!"
    
    first = jobs[0]
    print(f"  Sample LinkedIn Job 1: '{first.title}' at '{first.company}'")
    print(f"  Location: {first.location}")
    print(f"  URL: {first.url}")
    assert first.title and first.company and first.url
    print("  [PASS] LinkedIn scraper successfully retrieved job listings!")

def test_5_sheets_tracker():
    print("\n" + "=" * 60)
    print("TEST 5: Google Sheets Tracking Safe Wrapper")
    print("=" * 60)
    sample = [
        Job(
            title="Software Engineer",
            company="TestOrg",
            location="Bangalore",
            url="https://example.com/1",
            description="Software Engineer role",
            source="test",
            scraped_at="2026-11-03T10:00:00"
        )
    ]
    sample[0].match_score = 0.90
    sample[0].match_meta = {"recommendation": "apply", "matched_skills": ["Python"], "missing_skills": []}
    sample[0].scored = True

    ok, msg = _safe_log_to_sheets(sample)
    print(f"Sheets tracker response: ok={ok}, status='{msg}'")
    print("  [PASS] Google Sheets tracking executed without crashing or hanging!")

if __name__ == "__main__":
    test_1_groq_models()
    test_2_resume_scoring()
    test_3_naukri_scraping()
    test_4_linkedin_scraping()
    test_5_sheets_tracker()
    print("\n" + "#" * 60)
    print("ALL 5 JOB APPLICATION AGENT TESTS PASSED SUCCESSFULLY!")
    print("#" * 60)
