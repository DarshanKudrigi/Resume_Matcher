import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.schemas.job import JobParseRequest
from app.routers.jobs import parse_job_description

TEST_URLS = [
    # 1. Amazon Jobs
    ("Amazon Jobs", "https://www.amazon.jobs/en/jobs/10565307/snr-manager-design-engineering-india-data-center-engineering"),
    # 2. Microsoft Careers
    ("Microsoft Careers (PID 1)", "https://apply.careers.microsoft.com/careers?query=Software+Engineering&start=0&location=India&pid=1970393557026326&sort_by=relevance&filter_include_remote=1&filter_include_relocation=0"),
    ("Microsoft Careers (PID 2)", "https://apply.careers.microsoft.com/careers?query=Software+Engineering&start=0&location=India&pid=1970393556961685&sort_by=relevance&filter_include_remote=1&filter_include_relocation=0"),
    # 3. Lever
    ("Lever (Job 1)", "https://jobs.lever.co/drivetrain/d7808cbe-0c2f-47f0-9261-f10f6cfea9aa"),
    ("Lever (Job 2)", "https://jobs.lever.co/drivetrain/c677fe8d-8f9d-483e-b523-62c77e1a0fb7"),
    # 4. Edge Cases
    ("Invalid Protocol", "ftp://example.com/job/123"),
    ("Blocked Loopback", "http://localhost:8000/internal-job"),
]

async def run_live_tests():
    print("=" * 80)
    print("PHASE 1 LIVE URL EXTRACTION TEST SUITE")
    print("=" * 80)
    
    records = []

    for label, url in TEST_URLS:
        print(f"\n--- Testing: {label} ---")
        print(f"URL: {url}")
        
        req = JobParseRequest(url=url)
        try:
            res = await parse_job_description(req, db=None)
            record = {
                "label": label,
                "url": url,
                "domain": res.source,
                "accessible": "Yes",
                "identified": "Yes" if res.title and "Failed" not in res.title else "No",
                "title": res.title,
                "company": res.company,
                "location": res.location,
                "description": "Extracted" if res.description else "Missing",
                "responsibilities": "Extracted" if res.responsibilities else "Missing",
                "qualifications": "Extracted" if res.qualifications else "Missing",
                "required_skills": res.requiredSkills,
                "preferred_skills": res.preferredSkills,
                "unclassified_skills": res.unclassifiedSkills,
                "api_status": res.status,
                "warnings": res.warnings,
                "error": res.errorMessage
            }
            records.append(record)
            print(f"Status: {res.status.upper()}")
            print(f"Title: {res.title}")
            print(f"Company: {res.company}")
            print(f"Location: {res.location}")
            print(f"Required Skills ({len(res.requiredSkills)}): {res.requiredSkills}")
            print(f"Preferred Skills ({len(res.preferredSkills)}): {res.preferredSkills}")
            if res.unclassifiedSkills:
                print(f"Unclassified Skills ({len(res.unclassifiedSkills)}): {res.unclassifiedSkills}")
        except Exception as e:
            record = {
                "label": label,
                "url": url,
                "domain": "N/A",
                "accessible": "No",
                "identified": "No",
                "title": "",
                "company": "",
                "location": "",
                "description": "Missing",
                "responsibilities": "Missing",
                "qualifications": "Missing",
                "required_skills": [],
                "preferred_skills": [],
                "unclassified_skills": [],
                "api_status": "Error",
                "warnings": [],
                "error": str(e)
            }
            records.append(record)
            print(f"Status: ERROR ({e})")

    with open("phase1_test_results.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED. Results saved to backend/phase1_test_results.json")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_live_tests())

