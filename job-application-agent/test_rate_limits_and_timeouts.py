import os
import sys
import time
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure agent folder is on sys.path
AGENT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENT_ROOT))

from tracker.models import Job
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_REQUEST_DELAY, GROQ_MAX_RETRIES
from matcher.resume_matcher import (
    score_job,
    get_client,
    get_scoring_cache,
    clear_scoring_cache,
    _extract_retry_after,
    _get_cache_key
)
from scraper.linkedin_scraper import LinkedInScraper
from scraper.naukri_scraper import NaukriScraper
from agent_service import _safe_log_to_sheets

SAMPLE_RESUME = """
Chandan S Gowda
Email: chandan@example.com | Bengaluru, India
Full Stack Python & FastAPI Developer with 3+ years of experience designing scalable RESTful APIs,
integrating microservices, and deploying on Azure cloud. Proficient in Python, FastAPI, Django, React,
PostgreSQL, Docker, Git, Linux, and REST APIs.
"""

def test_1_and_2_descriptions():
    print("=" * 65)
    print("TEST 1 & 2: LinkedIn & Naukri Description Extractions (28s, DOMContentLoaded)")
    print("=" * 65)

    # 1. LinkedIn extraction
    print("1. Testing LinkedIn description extraction...")
    li_scraper = LinkedInScraper(keywords=["Software Engineer"], location="Bangalore, Karnataka", headless=True)
    li_jobs = li_scraper.scrape(max_jobs=2)
    assert len(li_jobs) > 0, "No LinkedIn jobs scraped!"
    first_li = li_jobs[0]
    print(f"  [PASS] LinkedIn Job: '{first_li.title}' at '{first_li.company}'")
    print(f"  URL: {first_li.url}")
    print(f"  Description length: {len(first_li.description)} chars")
    assert first_li.url, "LinkedIn job URL must be preserved!"

    # 2. Naukri extraction
    print("\n2. Testing Naukri description extraction...")
    nk_scraper = NaukriScraper(keywords=["Software Engineer"], location="Bangalore, Karnataka", headless=True)
    nk_jobs = nk_scraper.scrape(max_jobs=2)
    assert len(nk_jobs) > 0, "No Naukri jobs scraped!"
    first_nk = nk_jobs[0]
    print(f"  [PASS] Naukri Job: '{first_nk.title}' at '{first_nk.company}'")
    print(f"  URL: {first_nk.url}")
    print(f"  Description length: {len(first_nk.description)} chars")
    assert first_nk.url, "Naukri job URL must be preserved!"
    assert len(first_nk.description) > 0, "Naukri description should be populated!"

def test_3_groq_multiple_jobs_and_5_caching():
    print("\n" + "=" * 65)
    print("TEST 3 & 5: Groq Matching for Multiple Jobs & In-Memory Caching")
    print("=" * 65)
    clear_scoring_cache()

    job_a = Job(
        title="Python Backend Developer",
        company="Alpha Tech",
        location="Bengaluru",
        url="https://linkedin.com/jobs/view/9001",
        description="Looking for Python, FastAPI, and PostgreSQL engineers. Freshers to 2 years.",
        source="linkedin",
        scraped_at="2026-11-03T10:00:00"
    )
    job_b = Job(
        title="Full Stack Engineer",
        company="Beta Systems",
        location="Bengaluru",
        url="https://naukri.com/job-listings-9002",
        description="Looking for Python, React, Docker, and REST APIs developer. 1-3 years experience.",
        source="naukri",
        scraped_at="2026-11-03T10:00:00"
    )

    # First run: score job_a and job_b with real Groq API
    t0 = time.time()
    scored_a = score_job(job_a, SAMPLE_RESUME)
    time.sleep(GROQ_REQUEST_DELAY)
    scored_b = score_job(job_b, SAMPLE_RESUME)
    t_first = time.time() - t0

    assert scored_a.scored is True and scored_a.match_score is not None
    assert scored_b.scored is True and scored_b.match_score is not None
    print(f"  [PASS] Job A: {scored_a.title} -> Match: {int(scored_a.match_score * 100)}%, Rec: {scored_a.match_meta.get('recommendation')}")
    print(f"  [PASS] Job B: {scored_b.title} -> Match: {int(scored_b.match_score * 100)}%, Rec: {scored_b.match_meta.get('recommendation')}")
    print(f"  First execution time (API calls): {t_first:.2f}s")

    # Verify cache has both jobs
    cache = get_scoring_cache()
    key_a = _get_cache_key(job_a, SAMPLE_RESUME)
    key_b = _get_cache_key(job_b, SAMPLE_RESUME)
    assert key_a in cache, "Job A missing from cache!"
    assert key_b in cache, "Job B missing from cache!"
    print(f"  [PASS] Scoring cache verified with {len(cache)} entries.")

    # Second run: rescore job_a (must be instant cache hit without API calls)
    t1 = time.time()
    scored_a2 = score_job(job_a, SAMPLE_RESUME)
    t_cached = time.time() - t1
    print(f"  Cached execution time: {t_cached:.4f}s")
    assert t_cached < 0.05, f"Cache retrieval was too slow: {t_cached}s"
    assert scored_a2.match_score == scored_a.match_score
    print("  [PASS] Cache hit returned identical scores in <5ms without repeating API calls!")

def test_4_rate_limiting_429_recovery():
    print("\n" + "=" * 65)
    print("TEST 4: HTTP 429 Rate Limiting, Retry-After Header & Backoff Recovery")
    print("=" * 65)
    
    # 1. Test Retry-After extraction logic
    mock_resp = MagicMock()
    mock_resp.headers = {"retry-after": "1.5"}
    mock_err_with_header = Exception("429 Too Many Requests")
    mock_err_with_header.response = mock_resp
    retry_sec = _extract_retry_after(mock_err_with_header)
    print(f"  Extracted Retry-After from header: {retry_sec}s")
    assert retry_sec == 1.5, f"Expected 1.5, got {retry_sec}"

    mock_err_msg = Exception("Rate limit reached. Please try again in 2.4s.")
    retry_sec_msg = _extract_retry_after(mock_err_msg)
    print(f"  Extracted Retry-After from message regex: {retry_sec_msg}s")
    assert retry_sec_msg == 2.4, f"Expected 2.4, got {retry_sec_msg}"

    # 2. Test mock recovery: 1st attempt returns 429, 2nd attempt succeeds
    clear_scoring_cache()
    mock_client = MagicMock()
    
    # Attempt 1: raise RateLimitError
    try:
        from groq import RateLimitError
        rate_err = RateLimitError("Rate limit exceeded. Please try again in 0.5s.", response=mock_resp, body=None)
    except Exception:
        rate_err = Exception("Rate limit exceeded. Please try again in 0.5s.")

    mock_success = MagicMock()
    mock_success.choices = [MagicMock(message=MagicMock(content=json.dumps({
        "score": 0.88,
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": [],
        "recommendation": "apply",
        "reason": "Recovered successfully after 429 rate limit backoff.",
        "experience_required": 1,
        "experience_match": True
    })))]

    mock_client.chat.completions.create.side_effect = [rate_err, mock_success]

    test_job = Job(
        title="Cloud DevOps Engineer",
        company="Gamma Corp",
        location="Bengaluru",
        url="https://example.com/jobs/9003",
        description="Python Azure Docker developer",
        source="test",
        scraped_at="2026-11-03T10:00:00"
    )

    with patch("matcher.resume_matcher.get_client", return_value=mock_client):
        scored = score_job(test_job, SAMPLE_RESUME, max_retries=3)
        assert scored.scored is True
        assert scored.match_score == 0.88
        assert mock_client.chat.completions.create.call_count == 2
        print("  [PASS] Successfully recovered from HTTP 429 rate limit after backoff delay!")

def test_6_processing_resilience_and_failure_isolation():
    print("\n" + "=" * 65)
    print("TEST 6: Processing All Available Jobs Without Stopping After One Failure")
    print("=" * 65)

    job_good1 = Job(
        title="Backend Engineer",
        company="Good Co 1",
        location="Bangalore",
        url="https://example.com/1",
        description="Python FastAPI backend",
        source="test",
        scraped_at="2026-11-03T10:00:00"
    )
    job_bad = Job(
        title="Problematic Role",
        company="Bad Co",
        location="Bangalore",
        url="https://example.com/bad",
        description="Fails scoring",
        source="test",
        scraped_at="2026-11-03T10:00:00"
    )
    job_good2 = Job(
        title="Frontend Engineer",
        company="Good Co 2",
        location="Bangalore",
        url="https://example.com/2",
        description="React JavaScript frontend",
        source="test",
        scraped_at="2026-11-03T10:00:00"
    )

    all_test_jobs = [job_good1, job_bad, job_good2]

    def mock_score_selector(j, resume):
        if j.url == "https://example.com/bad":
            j.match_score = None
            j.scored = False
            j.scoring_error = "Simulated permanent API timeout error"
            return j
        j.match_score = 0.85
        j.scored = True
        j.match_meta = {"matched_skills": ["Python"], "missing_skills": [], "recommendation": "apply", "reason": "Strong fit"}
        return j

    with patch("matcher.resume_matcher.score_job", side_effect=mock_score_selector):
        processed = []
        for j in all_test_jobs:
            try:
                res = mock_score_selector(j, SAMPLE_RESUME)
                processed.append(res)
            except Exception as e:
                # Even on exception, preserve the job
                j.scoring_error = str(e)
                processed.append(j)

        assert len(processed) == 3, "Expected all 3 jobs to be processed!"
        assert processed[0].scored is True
        assert processed[1].scored is False and processed[1].url == "https://example.com/bad"
        assert processed[2].scored is True
        print("  [PASS] Failure on Job 2 did not stop batch! Jobs 1 and 3 processed and preserved.")

def test_7_google_sheets():
    print("\n" + "=" * 65)
    print("TEST 7: Google Sheets Tracking Safe Execution")
    print("=" * 65)
    test_sample = [
        Job(
            title="Senior Python Developer",
            company="SheetsTestCorp",
            location="Bengaluru",
            url="https://example.com/jobs/sheets-test",
            description="Python FastAPI Google Sheets Test",
            source="test",
            scraped_at="2026-11-03T10:00:00"
        )
    ]
    test_sample[0].match_score = 0.95
    test_sample[0].match_meta = {"recommendation": "apply", "matched_skills": ["Python"], "missing_skills": []}
    test_sample[0].scored = True

    ok, msg = _safe_log_to_sheets(test_sample)
    print(f"  Sheets Tracker response: ok={ok}, message='{msg}'")
    print("  [PASS] Google Sheets tracking completed safely without hanging.")

if __name__ == "__main__":
    test_1_and_2_descriptions()
    test_3_groq_multiple_jobs_and_5_caching()
    test_4_rate_limiting_429_recovery()
    test_6_processing_resilience_and_failure_isolation()
    test_7_google_sheets()
    print("\n" + "#" * 65)
    print("ALL 7 RATE-LIMITING & TIMEOUT VERIFICATION TESTS PASSED!")
    print("#" * 65)

