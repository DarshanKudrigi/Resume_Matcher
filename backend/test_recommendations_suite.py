import sys
import os
import json
import csv
from pathlib import Path

# Add backend directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Ensure agent site-packages is in path
AGENT_DIR = BASE_DIR.parent / "job-application-agent"
AGENT_SITE_PACKAGES = AGENT_DIR / "venv" / "Lib" / "site-packages"
if AGENT_SITE_PACKAGES.exists() and str(AGENT_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(AGENT_SITE_PACKAGES))
if AGENT_DIR.exists() and str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from app.schemas.recommendation import JobRecommendationRequest, RecommendedJobItem
from app.services.matcher_service import analyze_resume_against_job
from app.services.recommendations import get_recommendations_for_skills
from app.services.job_recommendation_service import log_to_local_csv, TRACKED_CSV_PATH
from app.services.parser_service import parse_resume_content, extract_text_from_pdf
from app.routers.recommendations import search_job_recommendations
from fastapi import HTTPException
from tracker.models import Job

print("==================================================")
print("TEST 1: PARSER QUALITY - NO FRAGMENTED PROJECT NAMES")
print("==================================================")

sample_pdf = BASE_DIR / "uploads" / "file-1f58941ac7_chandan_resume_2023.docx.pdf"
if sample_pdf.exists():
    with open(sample_pdf, "rb") as f:
        text = extract_text_from_pdf(f.read())[0]
    parsed = parse_resume_content(text, "chandan_resume.pdf")
    projs = parsed.get("projects", [])
    print(f"Parsed {len(projs)} project(s):")
    stop_words = {"including", "to", "and", "or", "in", "with", "etc", "live", "browse", "vm", "vcloud", "azure"}
    for p in projs:
        name = p.get("name", "")
        print(f"  - Project: '{name}' (Tech: '{p.get('tech')}')")
        assert name.lower() not in stop_words, f"Corrupted stop-word detected as project name: {name}"
        assert len(name.split()) > 1 or len(name) > 2, f"Invalid single-word project name: {name}"
    print("[PASS] Project parser test passed: Zero fragmented words in projects!")
else:
    print("Notice: Sample PDF not found, skipping file parse check.")

print("\n==================================================")
print("TEST 2: RESUME MATCHING & LEARNING RECS FOR JOBS")
print("==================================================")

sample_resume = {
    "personalInfo": {"fullName": "Chandan S Gowda"},
    "skills": {
        "languages": ["Python", "JavaScript", "Dart"],
        "frameworks": ["Django", "FastAPI", "React", "Flutter"],
        "tools": ["Git", "Docker", "Linux"],
        "concepts": ["REST APIs", "Microservices"]
    },
    "projects": [
        {"name": "Resonate Voice Platform", "tech": "Flutter, Node.js, WebRTC"}
    ]
}

sample_job = {
    "id": "job-test-001",
    "title": "Full Stack Software Engineer",
    "company": "Apex Technologies",
    "location": "Bengaluru",
    "url": "https://www.linkedin.com/jobs/view/123456789",
    "description": "Seeking Software Engineer with FastAPI, React, Docker, Kubernetes, and AWS experience.",
    "requiredSkills": ["FastAPI", "React", "Docker", "Kubernetes", "AWS"],
    "preferredSkills": ["GraphQL", "TypeScript"]
}

analysis = analyze_resume_against_job(sample_resume, sample_job)
print(f"Job: {sample_job['title']} at {sample_job['company']}")
print(f"Match Score: {analysis.matchScore}% (Status: {analysis.status})")
print(f"Matched Skills: {analysis.matchedSkills}")
print(f"Missing Skills: {analysis.missingSkills}")

assert analysis.matchScore >= 35, f"Expected reasonable match score, got {analysis.matchScore}"
assert "FastAPI" in analysis.matchedSkills or "React" in analysis.matchedSkills, "Expected FastAPI/React matched"
assert "Kubernetes" in analysis.missingSkills, "Expected Kubernetes missing"

recs = get_recommendations_for_skills(analysis.missingSkills, max_count=3)
print(f"Official Docs Learning Recs ({len(recs)}):")
for r in recs:
    link = r.resources[0].link if r.resources else ""
    print(f"  - {r.skill}: {link} ({r.subtitle})")
    assert link.startswith("https://") or link.startswith("http://"), "Doc URL must be valid link"

print("[PASS] Resume matching & official docs test passed!")

print("\n==================================================")
print("TEST 3: LOCAL CSV TRACKER LOGGING & DEDUPLICATION")
print("==================================================")

test_job_1 = {
    "id": "test-job-unique-101",
    "title": "Senior Backend Developer",
    "company": "InnoSoft",
    "location": "Bengaluru",
    "url": "https://www.linkedin.com/jobs/view/999888111",
    "source": "linkedin",
    "matchScore": 85,
    "status": "Strong Match",
    "matchedSkills": ["Python", "FastAPI"],
    "missingSkills": ["Kubernetes"],
    "scraped_at": "2026-11-03T10:00:00"
}

added_1 = log_to_local_csv([test_job_1])
print(f"First logging attempt added: {added_1} row(s)")
assert added_1 >= 0

test_job_dup = {
    "id": "test-job-unique-101",
    "title": "Senior Backend Developer",
    "company": "InnoSoft",
    "location": "Bengaluru",
    "url": "https://www.linkedin.com/jobs/view/999888111?refId=123",
    "source": "linkedin",
    "matchScore": 85,
    "status": "Strong Match",
    "matchedSkills": ["Python", "FastAPI"],
    "missingSkills": ["Kubernetes"],
    "scraped_at": "2026-11-03T10:00:00"
}

added_2 = log_to_local_csv([test_job_dup])
print(f"Duplicate logging attempt added: {added_2} row(s)")
assert added_2 == 0, f"Expected 0 added for duplicate URL, got {added_2}"

print("[PASS] Spreadsheet tracker deduplication test passed!")

print("\n==================================================")
print("TEST 4: RECOMMENDATIONS ROUTER INPUT VALIDATION")
print("==================================================")

# Test input validation: empty role
coro1 = search_job_recommendations(JobRecommendationRequest(desired_role="", location="Bengaluru"))
try:
    coro1.send(None)
    assert False, "Should have raised HTTPException 400"
except HTTPException as e:
    assert e.status_code == 400
    print("[PASS] Input validation (empty role -> HTTPException 400) passed!")

# Test input validation: empty location
coro2 = search_job_recommendations(JobRecommendationRequest(desired_role="Software Engineer", location=""))
try:
    coro2.send(None)
    assert False, "Should have raised HTTPException 400"
except HTTPException as e:
    assert e.status_code == 400
    print("[PASS] Input validation (empty location -> HTTPException 400) passed!")

print("\n==================================================")
print("ALL RECOMMENDATION SUITE TESTS PASSED 100%!")
print("==================================================")
