import os
import sys
import time
import json
import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

AGENT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENT_ROOT))

from tracker.models import Job
from config import GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TPM_LIMIT, GROQ_MAX_RETRIES
from matcher.resume_matcher import (
    score_job,
    filter_jobs,
    get_client,
    get_scoring_cache,
    clear_scoring_cache,
    compress_resume_for_matching,
    clean_and_truncate_jd,
    TokenUsageTracker,
    _extract_retry_after,
    _get_cache_key,
    CACHE_FILE
)

LONG_RAW_RESUME = """
John Doe
123 Main Street, Apt 4B, New York, NY 10001
Phone: +1 (555) 019-2834 | Email: john.doe@example.com | LinkedIn: linkedin.com/in/johndoe
Portfolio: https://johndoe.dev | GitHub: github.com/johndoe

SUMMARY
Enthusiastic and results-driven Software Engineer with extensive experience in architecting full-stack web applications,
designing distributed microservices, and implementing RESTful APIs. Adept at collaborating across cross-functional agile teams.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, Go, SQL, Bash, HTML5, CSS3
Frameworks & Libraries: FastAPI, Django, Flask, Express.js, React, Redux, Next.js, Node.js
Databases: PostgreSQL, MySQL, Redis, MongoDB, DynamoDB
Cloud & DevOps: AWS (EC2, S3, RDS, Lambda), Azure, Docker, Kubernetes, CI/CD pipelines, Git, GitHub Actions, Linux
Tools: Postman, JIRA, Confluence, VS Code, Webpack, Vite, Pytest, Jest

PROFESSIONAL EXPERIENCE
Senior Backend Engineer | Alpha Cloud Corp, New York, NY | June 2022 - Present
- Architected high-throughput backend services using Python FastAPI and PostgreSQL serving 1M+ active users.
- Reduced database query latency by 45% through indexing and Redis caching strategies.
- Designed and maintained RESTful APIs with automated OpenAPI documentation and JWT authentication.
- Led migration of on-prem monolithic architecture to containerized microservices using Docker and Kubernetes.

Software Engineer | Beta Solutions Inc, Boston, MA | January 2021 - May 2022
- Developed responsive web interfaces using React.js and integrated with Node.js / Express backend.
- Automated CI/CD deployment pipelines using GitHub Actions, reducing deployment time by 60%.
- Implemented unit and integration tests using Pytest and Jest with 90%+ code coverage.

EDUCATION
Bachelor of Science in Computer Science | Massachusetts Institute of Technology (MIT) | 2016 - 2020
Cumulative GPA: 3.9 / 4.0
Relevant Coursework: Data Structures & Algorithms, Database Systems, Computer Networks, Distributed Computing.

CERTIFICATIONS
- AWS Certified Solutions Architect - Associate
- Certified Kubernetes Administrator (CKA)

DECLARATION
I hereby declare that the above-mentioned details are true to the best of my knowledge and belief.
References available upon request.
"""

LONG_RAW_JD = """
About TechCorp Global:
TechCorp Global is a premier technology solutions provider with offices in 25 countries worldwide.
We believe in fostering an inclusive, collaborative culture where every engineer is empowered to innovate.
We are proud to be an Equal Opportunity Employer. All qualified applicants will receive consideration for employment
without regard to race, color, religion, sex, sexual orientation, gender identity, national origin, disability, or veteran status.

Position: Senior Python / FastAPI Engineer
Location: Bengaluru, India (Hybrid)

Role Overview:
We are looking for an experienced Senior Python Engineer to design, build, and maintain mission-critical cloud backend services.
You will collaborate with frontend engineers, product managers, and site reliability engineers.

Key Responsibilities:
- Design, develop, and maintain scalable REST APIs and microservices using Python, FastAPI, and PostgreSQL.
- Optimize application performance, scalability, and security across AWS cloud infrastructure.
- Write robust unit, integration, and performance tests to ensure high code quality.
- Collaborate with the data and frontend teams to deliver end-to-end customer features.

Requirements & Qualifications:
- 1 to 2 years of relevant software development experience in backend engineering.
- Proficient in Python, FastAPI, and relational databases (PostgreSQL or MySQL).
- Hands-on experience with Docker, Git, and RESTful API design.
- Familiarity with cloud platforms such as AWS or Azure.
- Bachelor's degree in Computer Science, Engineering, or equivalent practical experience.

What We Offer / Benefits & Perks:
- Comprehensive medical, dental, and vision insurance coverage.
- Competitive salary with annual performance bonuses and equity options.
- 401(k) retirement plan with 5% employer match.
- Flexible work hours and generous paid time off (PTO) policy.
- Free catered lunches, snacks, and gym membership reimbursement.
- Continuous learning stipends and conference attendance sponsorship.

Physical Demands:
Prolonged periods of sitting at a desk and working on a computer.

COVID-19 Vaccination Notice:
TechCorp adheres to all local health directives. Proof of vaccination may be requested where required by law.

Notice to Third-Party Agencies:
TechCorp does not accept unsolicited resumes from recruiters or staffing agencies without an executed agreement.
"""

def test_token_reduction():
    print("=" * 65)
    print("TEST 1: Token Reduction & Prompt Compaction")
    print("=" * 65)
    
    # Raw token approximation (~4 chars/token)
    raw_resume_tokens = len(LONG_RAW_RESUME) // 4
    raw_jd_tokens = len(LONG_RAW_JD) // 4
    raw_total_tokens = raw_resume_tokens + raw_jd_tokens
    print(f"  Raw Resume: {len(LONG_RAW_RESUME)} chars (~{raw_resume_tokens} tokens)")
    print(f"  Raw JD: {len(LONG_RAW_JD)} chars (~{raw_jd_tokens} tokens)")
    print(f"  Raw Combined Tokens: ~{raw_total_tokens} tokens (Before Prompt & Default Output)")

    # Compressed resume
    compressed_resume = compress_resume_for_matching(LONG_RAW_RESUME, max_chars=1500)
    cleaned_jd = clean_and_truncate_jd(LONG_RAW_JD, max_chars=1800)
    
    comp_resume_tokens = len(compressed_resume) // 4
    comp_jd_tokens = len(cleaned_jd) // 4
    comp_total_tokens = comp_resume_tokens + comp_jd_tokens
    print(f"\n  Compressed Resume: {len(compressed_resume)} chars (~{comp_resume_tokens} tokens)")
    print(f"  Cleaned JD: {len(cleaned_jd)} chars (~{comp_jd_tokens} tokens)")
    print(f"  Cleaned Combined Tokens: ~{comp_total_tokens} tokens")

    # Assertions on token reduction
    assert len(compressed_resume) <= 1500, f"Resume exceeded 1500 chars: {len(compressed_resume)}"
    assert len(cleaned_jd) <= 1800, f"JD exceeded 1800 chars: {len(cleaned_jd)}"
    assert "john.doe@example.com" not in compressed_resume, "Emails should be stripped!"
    assert "Equal Opportunity Employer" not in cleaned_jd, "EEO boilerplate should be stripped!"
    assert "401(k) retirement plan" not in cleaned_jd, "Benefits/Perks boilerplate should be stripped!"
    assert "Notice to Third-Party Agencies" not in cleaned_jd, "Agency notices should be stripped!"

    # Ensure key technical skills and requirements survived
    assert "Python" in compressed_resume and "FastAPI" in compressed_resume
    assert "FastAPI" in cleaned_jd and "PostgreSQL" in cleaned_jd
    
    reduction_pct = (1.0 - (comp_total_tokens / raw_total_tokens)) * 100
    print(f"  [PASS] Prompt compaction achieved {reduction_pct:.1f}% token reduction!")
    print(f"  [PASS] Configured GROQ_MAX_TOKENS = {GROQ_MAX_TOKENS} (prevents 2000+ default reservation)")


def test_token_usage_tracker_sliding_window():
    print("\n" + "=" * 65)
    print("TEST 2: TokenUsageTracker Sliding-Window TPM Throttling")
    print("=" * 65)
    
    # Create tracker with 8000 limit, 1000 buffer (effective = 7000)
    tracker = TokenUsageTracker(tpm_limit=8000, safety_buffer=1000)
    assert tracker.effective_limit == 7000
    
    now = time.time()
    # Add simulated usages
    tracker.history.append((now - 30.0, 3000))
    tracker.history.append((now - 10.0, 3200))
    
    used = tracker.get_used_tokens_last_minute(now)
    print(f"  Simulated tokens used in last 60s: {used} / {tracker.effective_limit}")
    assert used == 6200
    
    # Request that fits (700 tokens -> 6900 <= 7000)
    waited = tracker.wait_for_tpm_budget(700)
    assert waited == 0.0, f"Should not wait when within budget, waited {waited}s"
    print("  [PASS] Request within TPM budget passed immediately without waiting.")
    
    # Request that would breach (1000 tokens -> 7200 > 7000)
    # The oldest record is at (now - 30.0), so it expires in (now - 30 + 60) - now = 30 seconds.
    # To test without waiting 30 real seconds, simulate aging the oldest record to now - 59.5
    tracker.history[0] = (now - 59.5, 3000)
    t_start = time.time()
    waited_throttle = tracker.wait_for_tpm_budget(1000)
    t_elapsed = time.time() - t_start
    print(f"  Throttling wait time for expiring window: {waited_throttle:.2f}s (actual {t_elapsed:.2f}s)")
    assert waited_throttle > 0.0
    print("  [PASS] Successfully paused to protect Groq TPM budget from HTTP 429!")


def test_single_retry_and_rate_limit_recovery():
    print("\n" + "=" * 65)
    print("TEST 3: Single Retry Loop (No SDK Retries) & Retry-After Recovery")
    print("=" * 65)
    clear_scoring_cache()
    
    # 1. Verify get_client has max_retries=0
    client = get_client()
    sdk_max_retries = getattr(client, "max_retries", None)
    print(f"  Groq SDK client max_retries configured: {sdk_max_retries}")
    assert sdk_max_retries == 0, f"Expected SDK max_retries=0 to avoid overlapping retries, got {sdk_max_retries}"

    # 2. Mock 429 rate limit with Retry-After header
    mock_resp = MagicMock()
    mock_resp.headers = {"retry-after": "0.5"}
    
    try:
        from groq import RateLimitError
        rate_err = RateLimitError("Rate limit reached. Try again in 0.5s.", response=mock_resp, body=None)
    except Exception:
        rate_err = Exception("Rate limit reached. Try again in 0.5s.")

    mock_success = MagicMock()
    mock_success.choices = [MagicMock(message=MagicMock(content=json.dumps({
        "score": 0.90,
        "matched_skills": ["Python", "FastAPI", "PostgreSQL"],
        "missing_skills": ["AWS"],
        "recommendation": "apply",
        "reason": "Strong match on core backend stack.",
        "experience_required": 1,
        "experience_match": True
    })))]
    mock_success.usage = MagicMock(total_tokens=420)

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [rate_err, mock_success]

    test_job = Job(
        title="Senior Python / FastAPI Engineer",
        company="TechCorp Global",
        location="Bengaluru",
        url="https://example.com/jobs/fastapi-101",
        description=LONG_RAW_JD,
        source="linkedin",
        scraped_at="2026-11-03T10:00:00"
    )

    with patch("matcher.resume_matcher.get_client", return_value=mock_client):
        scored = score_job(test_job, LONG_RAW_RESUME, max_retries=3)
        assert scored.scored is True
        assert scored.match_score == 0.90
        assert mock_client.chat.completions.create.call_count == 2
        print("  [PASS] Recovered on attempt 2 after HTTP 429 with single controlled retry loop!")


def test_dual_caching_and_retry_only_failed():
    print("\n" + "=" * 65)
    print("TEST 4: Dual-Layer Caching (Memory + Disk) & Only Retrying Failed Jobs")
    print("=" * 65)
    clear_scoring_cache()
    
    job_ok = Job(
        title="FastAPI Developer",
        company="Alpha Ltd",
        location="Bengaluru",
        url="https://example.com/jobs/fastapi-alpha",
        description="Python FastAPI PostgreSQL",
        source="linkedin",
        scraped_at="2026-11-03T10:00:00"
    )
    job_fail = Job(
        title="Problematic Role",
        company="Broken Corp",
        location="Bengaluru",
        url="https://example.com/jobs/broken-role",
        description="Permanently failing JD",
        source="naukri",
        scraped_at="2026-11-03T10:00:00"
    )

    mock_success = MagicMock()
    mock_success.choices = [MagicMock(message=MagicMock(content=json.dumps({
        "score": 0.85,
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": [],
        "recommendation": "apply",
        "reason": "Great fit.",
        "experience_required": 1,
        "experience_match": True
    })))]
    mock_success.usage = MagicMock(total_tokens=380)

    mock_client = MagicMock()
    # First call: job_ok succeeds, job_fail raises 3 errors and fails
    mock_client.chat.completions.create.side_effect = [
        mock_success,
        Exception("API outage 1"),
        Exception("API outage 2"),
        Exception("API outage 3")
    ]

    with patch("matcher.resume_matcher.get_client", return_value=mock_client):
        scored_ok = score_job(job_ok, LONG_RAW_RESUME)
        scored_fail = score_job(job_fail, LONG_RAW_RESUME, max_retries=3)

    assert scored_ok.scored is True
    assert scored_fail.scored is False
    assert scored_fail.match_score == 0.5  # Safe preserved score
    print("  First run completed: Job OK scored=True, Job Fail scored=False.")

    # Verify cache: job_ok is cached, job_fail is NOT cached
    cache = get_scoring_cache()
    assert len(cache) == 1, f"Expected 1 cached job, got {len(cache)}"
    assert CACHE_FILE.exists(), "Persistent cache file should exist on disk!"
    print("  [PASS] Successful job cached to memory and disk. Failed job excluded from cache.")

    # Second run (Retrying the batch):
    # job_ok should hit cache (0 API calls)
    # job_fail should be the ONLY one that makes an API call!
    mock_success_2 = MagicMock()
    mock_success_2.choices = [MagicMock(message=MagicMock(content=json.dumps({
        "score": 0.75,
        "matched_skills": ["Python"],
        "missing_skills": [],
        "recommendation": "maybe",
        "reason": "Recovered on retry run.",
        "experience_required": 1,
        "experience_match": True
    })))]
    mock_success_2.usage = MagicMock(total_tokens=350)
    mock_client.chat.completions.create.side_effect = [mock_success_2]

    with patch("matcher.resume_matcher.get_client", return_value=mock_client):
        t0 = time.time()
        res_ok = score_job(job_ok, LONG_RAW_RESUME)
        t_cache = time.time() - t0
        assert t_cache < 0.05, f"Cache retrieval took {t_cache:.4f}s"
        assert res_ok.match_score == 0.85
        print(f"  [PASS] Cached job returned in {t_cache*1000:.2f}ms without API call.")

        # Retry failed job — this time it succeeds!
        res_fail_retry = score_job(job_fail, LONG_RAW_RESUME)
        assert res_fail_retry.scored is True
        assert res_fail_retry.match_score == 0.75
        print("  [PASS] Only the previously failed job was retried and scored successfully!")


def test_20_jobs_batch_resilience():
    print("\n" + "=" * 65)
    print("TEST 5: Full 20-Job Batch Execution Within Rate Limits")
    print("=" * 65)
    clear_scoring_cache()
    
    # Generate 10 LinkedIn and 10 Naukri jobs
    jobs = []
    for i in range(10):
        jobs.append(Job(
            title=f"LinkedIn Software Engineer {i+1}",
            company=f"LinkedIn Tech {i+1}",
            location="Bengaluru",
            url=f"https://linkedin.com/jobs/view/test-li-{i+1}",
            description=f"Python FastAPI React engineer role {i+1}",
            source="linkedin",
            scraped_at="2026-11-03T10:00:00"
        ))
    for i in range(10):
        jobs.append(Job(
            title=f"Naukri Full Stack Developer {i+1}",
            company=f"Naukri Corp {i+1}",
            location="Bengaluru",
            url=f"https://naukri.com/job-listings-test-nk-{i+1}",
            description=f"Python PostgreSQL Docker developer role {i+1}",
            source="naukri",
            scraped_at="2026-11-03T10:00:00"
        ))

    assert len(jobs) == 20
    print(f"  Created test batch: 10 LinkedIn + 10 Naukri = {len(jobs)} jobs total.")

    # Mock client with token tracking to verify rate limits
    total_tokens_simulated = 0
    def mock_create(*args, **kwargs):
        nonlocal total_tokens_simulated
        total_tokens_simulated += 450
        resp = MagicMock()
        resp.choices = [MagicMock(message=MagicMock(content=json.dumps({
            "score": 0.82,
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": [],
            "recommendation": "apply",
            "reason": "Consistent high match.",
            "experience_required": 1,
            "experience_match": True
        })))]
        resp.usage = MagicMock(total_tokens=450)
        return resp

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = mock_create

    with patch("matcher.resume_matcher.get_client", return_value=mock_client):
        scored_batch = []
        for j in jobs:
            res = score_job(j, LONG_RAW_RESUME)
            scored_batch.append(res)

    assert len(scored_batch) == 20
    for j in scored_batch:
        assert j.scored is True
        assert 0.0 <= j.match_score <= 1.0
        assert j.url and j.title and j.company

    print(f"  [PASS] All 20 jobs successfully scored! Total simulated tokens: {total_tokens_simulated}")
    print(f"  Average tokens per job: {total_tokens_simulated / 20:.0f} tokens (well under 8,000 TPM limit)")
    
    # Cleanup test cache
    clear_scoring_cache()


if __name__ == "__main__":
    test_token_reduction()
    test_token_usage_tracker_sliding_window()
    test_single_retry_and_rate_limit_recovery()
    test_dual_caching_and_retry_only_failed()
    test_20_jobs_batch_resilience()
    print("\n" + "#" * 65)
    print("ALL 5 TPM RATE LIMITING & TOKEN REDUCTION TESTS PASSED!")
    print("#" * 65)

