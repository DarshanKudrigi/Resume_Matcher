import sys
import os
import json
import asyncio
from pathlib import Path
from unittest.mock import patch

# Setup paths
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

# Ensure stdout is unbuffered
sys.stdout.reconfigure(line_buffering=True)

from app.schemas.analysis import AnalysisResponse, SkillGapItem, ATSBreakdown, ATSItem
from app.schemas.recommendation import JobRecommendationRequest, RecommendedJobItem
from app.services.matcher_service import analyze_resume_against_job
from app.services.job_recommendation_service import JobRecommendationService
from app.services.job_extraction.url_classifier import validate_and_sanitize_url, classify_job_url
from tracker.models import Job

def test_analysis_response_model():
    print("--- Test 1: AnalysisResponse Pydantic Model Attributes ---")
    ats_breakdown = ATSBreakdown(
        score=85,
        verdict="Strong",
        items=[ATSItem(id="1", label="Keywords", passed=True, note="Matches key skills")]
    )
    ar = AnalysisResponse(
        jobTitle="Senior Software Engineer",
        company="TechCorp",
        matchScore=88,
        atsScore=85,
        status="Strong Match",
        summary="Candidate matches core competencies.",
        matchedSkills=["Python", "FastAPI"],
        missingSkills=["Docker"],
        partialSkills=["Kubernetes"],
        matchedPreferredSkills=["FastAPI"],
        missingPreferredSkills=["Docker"],
        skillGaps=[],
        learningRecommendations=[],
        atsBreakdown=ats_breakdown
    )

    assert hasattr(ar, "matchedPreferredSkills"), "matchedPreferredSkills missing on AnalysisResponse!"
    assert hasattr(ar, "missingPreferredSkills"), "missingPreferredSkills missing on AnalysisResponse!"
    assert ar.matchedPreferredSkills == ["FastAPI"]
    assert ar.missingPreferredSkills == ["Docker"]
    print("[PASS] AnalysisResponse created and attributes verified successfully!\n")

def test_matcher_service_integration():
    print("--- Test 2: Matcher Service analyze_resume_against_job ---")
    resume_data = {
        "skills": {
            "languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React"],
            "tools": ["Git"]
        }
    }
    job_data = {
        "title": "Full Stack Engineer",
        "company": "Cloud Inc",
        "requiredSkills": ["Python", "Docker"],
        "preferredSkills": ["FastAPI", "AWS"],
        "description": "Looking for Python, Docker, FastAPI, AWS developers."
    }

    analysis = analyze_resume_against_job(resume_data, job_data, resume_raw_text="Python FastAPI Git")

    assert hasattr(analysis, "matchedPreferredSkills"), "matchedPreferredSkills missing on analysis result!"
    assert hasattr(analysis, "missingPreferredSkills"), "missingPreferredSkills missing on analysis result!"
    print(f"Matched Skills: {analysis.matchedSkills}")
    print(f"Missing Skills: {analysis.missingSkills}")
    print(f"Matched Preferred Skills: {analysis.matchedPreferredSkills}")
    print(f"Missing Preferred Skills: {analysis.missingPreferredSkills}")
    assert "FastAPI" in analysis.matchedPreferredSkills, "FastAPI should be in matchedPreferredSkills!"
    assert "AWS" in analysis.missingPreferredSkills, "AWS should be in missingPreferredSkills!"
    print("[PASS] Matcher service correctly computes and populates matchedPreferredSkills and missingPreferredSkills!\n")

def test_url_sanitizer_and_no_protocol():
    print("--- Test 3: URL Sanitizer & No Protocol Handling ---")
    with patch("socket.getaddrinfo") as mock_dns:
        mock_dns.return_value = [(2, 1, 0, '', ('93.184.216.34', 0))]
        # Missing protocol should auto-prefix https://
        parsed1 = validate_and_sanitize_url("linkedin.com/jobs/view/987654321")
        assert parsed1.scheme == "https", f"Expected https scheme, got {parsed1.scheme}"
        assert parsed1.netloc == "linkedin.com"
        print("[PASS] Successfully normalized URL without protocol to https://")

        # Standard valid url
        parsed2 = validate_and_sanitize_url("https://careers.google.com/jobs/123")
        assert parsed2.scheme == "https"
        assert parsed2.netloc == "careers.google.com"

        # Localhost / Loopback SSRF prevention
        try:
            validate_and_sanitize_url("http://127.0.0.1:8000/api")
            assert False, "Should have blocked 127.0.0.1"
        except ValueError as ve:
            print(f"[PASS] Security check correctly blocked localhost: {ve}")

    print("[PASS] URL sanitizer correctly auto-prefixes protocol and blocks SSRF targets!\n")

def test_naukri_url_building():
    print("--- Test 4: Naukri URL Slug Sanitization ---")
    from scraper.naukri_scraper import NaukriScraper
    scraper = NaukriScraper(keywords=["Software Engineer"], location="Bangalore, Karnataka")
    url = scraper._build_url()
    print("Constructed Naukri URL:", url)
    assert "," not in url, f"Naukri URL must not contain commas! Got: {url}"
    assert "software-engineer" in url
    assert "bangalore" in url
    print("[PASS] Naukri URL builder successfully sanitizes city and removes commas!\n")

async def test_recommendations_streaming_generator():
    print("--- Test 5: Recommendation Streaming Generator Reliability ---")
    
    # Mock scraper to return sample jobs immediately
    sample_jobs = [
        Job(
            title="Senior Python Backend Developer",
            company="FinTech Solutions",
            location="Bangalore, Karnataka",
            url="https://www.linkedin.com/jobs/view/1001",
            description="We need Python, FastAPI, Docker, and PostgreSQL developers.",
            source="linkedin",
            scraped_at="2026-11-03T10:00:00"
        ),
        Job(
            title="AI/ML Python Engineer",
            company="NexGen AI",
            location="Bangalore, Karnataka",
            url="https://www.naukri.com/job-listings-2002",
            description="Looking for Python, FastAPI, Machine Learning, and AWS.",
            source="naukri",
            scraped_at="2026-11-03T10:00:00"
        )
    ]
    for j in sample_jobs:
        j.match_meta = {"salary": "₹18-25 LPA", "experience": "2-4 Yrs", "posted_date": "1 day ago"}

    req = JobRecommendationRequest(
        desired_role="Python Developer",
        location="Bangalore, Karnataka",
        platforms=["linkedin", "naukri"],
        limit=10,
        resume_data={
            "skills": {
                "languages": ["Python", "SQL"],
                "frameworks": ["FastAPI"]
            }
        },
        resume_text="Python FastAPI backend developer with SQL expertise."
    )

    with patch("app.services.job_recommendation_service._run_scraper_sync") as mock_scrape, \
         patch("app.services.job_recommendation_service.log_to_google_sheets", return_value=(False, "Mocked sheets tracker")):
        mock_scrape.side_effect = lambda plat, role, loc, limit: (
            [j for j in sample_jobs if j.source == plat], None
        )

        events = []
        async for raw_event in JobRecommendationService.stream_recommendations(req):
            if raw_event.startswith("data: "):
                payload = json.loads(raw_event[6:].strip())
                events.append(payload)

        steps_seen = [e.get("step") for e in events]
        print(f"Total SSE Events Received: {len(events)}")
        print(f"Steps sequence: {steps_seen}")

        assert 1 in steps_seen, "Step 1 (Resume Processing) missing!"
        assert 2 in steps_seen, "Step 2 (LinkedIn Search) missing!"
        assert 3 in steps_seen, "Step 3 (Naukri Search) missing!"
        assert 4 in steps_seen, "Step 4 (Job Details) missing!"
        assert 5 in steps_seen, "Step 5 (AI Matching) missing!"
        assert 6 in steps_seen, "Step 6 (Search Completed) missing!"

        final_event = [e for e in events if e.get("step") == 6][-1]
        assert final_event["status"] == "completed"
        jobs_found = final_event["data"]["jobs"]
        print(f"Final Event Message: {final_event['message']}")
        print(f"Total jobs ranked & formatted: {len(jobs_found)}")
        
        # Verify job item attributes
        first_job = jobs_found[0]
        print("First ranked job:", first_job["title"], f"(Match: {first_job['matchScore']}%)")
        print("  Matched Skills:", first_job["matchedSkills"])
        print("  Missing Skills:", first_job["missingSkills"])
        print("  Matched Preferred Skills:", first_job["matchedPreferredSkills"])
        print("  Missing Preferred Skills:", first_job["missingPreferredSkills"])
        
        assert "matchedPreferredSkills" in first_job
        assert "missingPreferredSkills" in first_job
        assert first_job["matchScore"] > 0
        print("[PASS] Recommendation streaming generator executed reliably with 0 errors!")

async def main():
    test_analysis_response_model()
    test_matcher_service_integration()
    test_url_sanitizer_and_no_protocol()
    test_naukri_url_building()
    await test_recommendations_streaming_generator()
    print("\n" + "="*60)
    print("ALL 5 CORE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("="*60)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
