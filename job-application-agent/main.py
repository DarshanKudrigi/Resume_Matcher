import os
import time
from scraper.linkedin_scraper import LinkedInScraper
from scraper.naukri_scraper import NaukriScraper
from matcher.resume_matcher import score_job, filter_jobs
from notifier.email_notifier import send_daily_digest
from tracker.sheets_tracker import log_jobs
from config import KEYWORDS, LOCATION, MATCH_THRESHOLD, AUTO_APPLY_THRESHOLD

def load_resume() -> str:
    candidates = [
        "resume.txt",
        os.path.join(os.path.dirname(__file__), "resume.txt"),
        os.path.join(os.path.dirname(__file__), "..", "resume.txt"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    raise FileNotFoundError("Could not find 'resume.txt'. Please ensure resume.txt is present in the project directory.")

def run_pipeline():
    print("=" * 60)
    print("🤖 JOB AGENT PIPELINE STARTING")
    print("=" * 60)

    resume_text = load_resume()
    all_jobs = []

    # Step 1: Scrape all portals
    print(f"\n[1/4] Scraping job portals...")

    try:
        print("  → LinkedIn")
        linkedin = LinkedInScraper(keywords=KEYWORDS, location=LOCATION)
        linkedin_jobs = linkedin.scrape(max_jobs=10)
        print(f"     Found {len(linkedin_jobs)} job(s)")
        all_jobs.extend(linkedin_jobs)
    except Exception as e:
        print(f"  [ERROR] LinkedIn scraping failed: {e}")

    try:
        print("  → Naukri")
        naukri = NaukriScraper(keywords=KEYWORDS, location=LOCATION)
        naukri_jobs = naukri.scrape(max_jobs=10)
        print(f"     Found {len(naukri_jobs)} job(s)")
        all_jobs.extend(naukri_jobs)
    except Exception as e:
        print(f"  [ERROR] Naukri scraping failed: {e}")

    print(f"\n  Total scraped: {len(all_jobs)} job(s) across portals")
    if not all_jobs:
        print("  No jobs scraped. Exiting pipeline.")
        return

    # Step 2: Score
    print(f"\n[2/4] Scoring {len(all_jobs)} job(s) against your resume...")
    scored_count = 0
    failed_count = 0

    for i, job in enumerate(all_jobs):
        scored_job = score_job(job, resume_text)
        all_jobs[i] = scored_job
        if scored_job.scored and scored_job.match_score is not None:
            scored_count += 1
            rec = scored_job.match_meta.get("recommendation", "").upper()
            print(f"      [{i+1}/{len(all_jobs)}] [{rec} {scored_job.match_score:.0%}] {scored_job.title} at {scored_job.company} [{scored_job.source}]")
        else:
            failed_count += 1
            print(f"      [{i+1}/{len(all_jobs)}] [FAILED] {scored_job.title} at {scored_job.company} [{scored_job.source}]")
        time.sleep(0.3)

    print(f"\n  Scoring results: {scored_count} succeeded, {failed_count} failed")

    # Step 3: Filter + Log
    print(f"\n[3/4] Filtering and logging to Google Sheets...")
    good_jobs = filter_jobs(all_jobs, threshold=MATCH_THRESHOLD)
    print(f"      {len(good_jobs)} job(s) passed threshold ({MATCH_THRESHOLD:.0%}) out of {scored_count} scored")
    log_jobs(good_jobs, min_threshold=MATCH_THRESHOLD)

    # Step 4: Send email digest for high scoring jobs
    print(f"\n[4/4] Sending email digest (auto-apply threshold: {AUTO_APPLY_THRESHOLD:.0%})...")
    high_score_jobs = [j for j in good_jobs if j.match_score is not None and j.match_score >= AUTO_APPLY_THRESHOLD]
    send_daily_digest(high_score_jobs)

    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE — SUMMARY")
    print("=" * 60)
    if good_jobs:
        for job in good_jobs:
            rec = job.match_meta.get("recommendation", "").upper()
            score_str = f"{job.match_score:.0%}" if job.match_score is not None else "N/A"
            print(f"  [{rec}] {score_str} | {job.title} at {job.company} [{job.source}]")
    else:
        if failed_count > 0 and scored_count == 0:
            print("  No jobs qualified because AI scoring encountered errors for all jobs.")
        else:
            print("  No scraped jobs met the matching threshold today.")

    print(f"\nTotal logged to sheet: {len(good_jobs)}")
    print(f"Total qualifying for digest: {len(high_score_jobs)}")
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline()