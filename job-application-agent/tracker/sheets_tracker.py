import os
from typing import Optional
import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEET_NAME, GOOGLE_CREDENTIALS_PATH, MATCH_THRESHOLD
from tracker.models import Job

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

HEADERS = [
    "ID", "Title", "Company", "Location", "URL",
    "Source", "Match Score", "Recommendation",
    "Matched Skills", "Missing Skills", "Status", "Scraped At"
]


def get_credentials_path() -> str:
    """Find the valid service account credentials file across expected locations."""
    candidates = [
        GOOGLE_CREDENTIALS_PATH,
        "credentials.json",
        os.path.join(os.path.dirname(__file__), "..", "credentials.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "credentials.json"),
        "credentials.json.json",
        os.path.join(os.path.dirname(__file__), "..", "credentials.json.json"),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return os.path.abspath(candidate)
    raise FileNotFoundError(
        "Could not find Google Sheets credentials file ('credentials.json'). "
        "Please ensure credentials.json is placed in the project folder."
    )


def get_sheet():
    """Authorize and return the worksheet instance."""
    creds_path = get_credentials_path()
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sheet_name = GOOGLE_SHEET_NAME or "Job Applications"
    return gc.open(sheet_name).sheet1


def setup_headers(sheet=None):
    """Ensure headers exist in row 1 without clearing or disturbing existing data."""
    if sheet is None:
        sheet = get_sheet()
    try:
        first_row = sheet.row_values(1)
        if not first_row:
            sheet.insert_row(HEADERS, 1)
            print("Headers initialized in sheet.")
    except Exception as e:
        print(f"Warning: Could not verify or set up sheet headers: {e}")


def get_existing_ids(sheet=None) -> set:
    """Return all existing job IDs from column 1."""
    if sheet is None:
        sheet = get_sheet()
    ids = sheet.col_values(1)[1:]  # skip header
    return set(ids)


def log_jobs(jobs: list[Job], min_threshold: Optional[float] = None):
    """Batch-append successfully scored jobs that meet threshold without duplicating."""
    # Only consider jobs that were successfully scored
    valid_jobs = [
        j for j in jobs
        if j.scored and j.match_score is not None and (min_threshold is None or j.match_score >= min_threshold)
    ]

    if not valid_jobs:
        print("  No successfully scored jobs qualify for logging.")
        return

    try:
        sheet = get_sheet()
        setup_headers(sheet)

        # Retrieve existing IDs and URLs to robustly detect duplicates
        existing_ids = set(sheet.col_values(1)[1:])
        raw_urls = sheet.col_values(5)[1:] if len(HEADERS) >= 5 else []
        existing_urls = {
            u.strip().split("?")[0].rstrip("/").lower()
            for u in raw_urls if u
        }

        rows_to_add = []
        for job in valid_jobs:
            clean_url = (job.url or "").strip().split("?")[0].rstrip("/").lower()
            if job.id in existing_ids or (clean_url and clean_url in existing_urls):
                print(f"  Skipping duplicate: {job.title} at {job.company}")
                continue

            score_str = f"{job.match_score:.0%}" if job.match_score is not None else ""
            rows_to_add.append([
                job.id,
                job.title,
                job.company,
                job.location,
                job.url,
                job.source,
                score_str,
                job.match_meta.get("recommendation", ""),
                ", ".join(job.match_meta.get("matched_skills", [])),
                ", ".join(job.match_meta.get("missing_skills", [])),
                job.status,
                job.scraped_at,
            ])
            print(f"  Logged: {job.title} at {job.company} ({score_str})")

        if rows_to_add:
            sheet.append_rows(rows_to_add)
            print(f"  Successfully wrote {len(rows_to_add)} row(s) to Google Sheets.")
        else:
            print("  No new unique jobs to log (all candidates already logged).")

    except Exception as e:
        print(f"  [ERROR] Google Sheets logging failed ({type(e).__name__}): {e}")


def log_job(job: Job):
    log_jobs([job])


def clear_sheet(confirm: bool = False):
    """Clear all data from the sheet. Requires explicit confirm=True to prevent accidental data loss."""
    if not confirm:
        print("clear_sheet() skipped: confirmation required (confirm=True). Existing data preserved.")
        return

    try:
        sheet = get_sheet()
        sheet.clear()
        setup_headers(sheet)
        print("Sheet cleared and headers reset.")
    except Exception as e:
        print(f"Failed to clear sheet: {e}")


def update_job_status(job_id: str, new_status: str):
    """Update the status of a specific job by ID in Google Sheets."""
    try:
        sheet = get_sheet()
        cell = sheet.find(job_id)
        if cell:
            status_col = HEADERS.index("Status") + 1
            sheet.update_cell(cell.row, status_col, new_status)
            print(f"Updated {job_id} to '{new_status}'")
        else:
            print(f"Job ID {job_id} not found in sheet")
    except Exception as e:
        print(f"Failed to update job status in sheet: {e}")