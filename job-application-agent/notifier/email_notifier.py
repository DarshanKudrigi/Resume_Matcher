import json
import os
from typing import Set
import resend
from config import GMAIL_ADDRESS, RESEND_API_KEY
from tracker.models import Job

_NOTIFIED_JOBS_FILE = os.path.join(os.path.dirname(__file__), "..", ".notified_jobs.json")


def _get_notified_job_ids() -> Set[str]:
    """Load previously notified job IDs from local cache file."""
    if os.path.exists(_NOTIFIED_JOBS_FILE):
        try:
            with open(_NOTIFIED_JOBS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
        except Exception:
            return set()
    return set()


def _save_notified_job_ids(ids: Set[str]):
    """Save notified job IDs to local cache file."""
    try:
        with open(_NOTIFIED_JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(ids)), f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save notified job IDs cache: {e}")


def send_daily_digest(jobs: list[Job], allow_duplicates: bool = False):
    """Send an email digest of qualifying jobs.
    
    Prevents duplicate notifications for previously emailed jobs unless
    allow_duplicates is explicitly True. Gracefully skips if credentials
    are not configured.
    """
    if not jobs:
        print("  [Notice] No high-scoring jobs qualify for the email digest.")
        return

    # Filter out unscored / failed jobs
    valid_jobs = [j for j in jobs if j.scored and j.match_score is not None]
    if not valid_jobs:
        print("  [Notice] No successfully scored jobs to include in email digest.")
        return

    # Check for duplicates
    notified_ids = _get_notified_job_ids()
    new_jobs = [j for j in valid_jobs if allow_duplicates or j.id not in notified_ids]

    if not new_jobs:
        print(f"  [Notice] All {len(valid_jobs)} qualifying job(s) were previously notified. Skipping duplicate email.")
        return

    # Check email configuration
    api_key = (RESEND_API_KEY or os.getenv("RESEND_API_KEY") or "").strip()
    recipient = (GMAIL_ADDRESS or os.getenv("GMAIL_ADDRESS") or "").strip()

    if not api_key:
        print("  [Notice] Email notification skipped: RESEND_API_KEY is not configured in .env.")
        return

    if not recipient:
        print("  [Notice] Email notification skipped: GMAIL_ADDRESS is not configured in .env.")
        return

    resend.api_key = api_key
    subject = f"🤖 Job Agent — {len(new_jobs)} new job(s) need your review today"
    body = _build_email_body(new_jobs)

    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": [recipient],
            "subject": subject,
            "html": body,
        })
        print(f"  [SUCCESS] Email sent to {recipient} — {len(new_jobs)} new job(s) included.")

        # Update cache of notified IDs
        for j in new_jobs:
            notified_ids.add(j.id)
        _save_notified_job_ids(notified_ids)

    except Exception as e:
        print(f"  [ERROR] Email failed to send ({type(e).__name__}): {e}")


def _build_email_body(jobs: list[Job]) -> str:
    rows = ""
    for job in jobs:
        rec = job.match_meta.get("recommendation", "APPLY").upper()
        score = f"{job.match_score:.0%}" if job.match_score is not None else "N/A"
        matched = ", ".join(job.match_meta.get("matched_skills", [])) or "None listed"
        missing = ", ".join(job.match_meta.get("missing_skills", [])) or "None listed"
        color = "#4caf82" if rec == "APPLY" else "#f0a500"

        location_display = f" · {job.location}" if job.location else ""
        job_url = job.url or "#"

        rows += f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid #eee;">
                <strong>{job.title}</strong><br>
                <span style="color:#666;">{job.company}{location_display}</span>
            </td>
            <td style="padding:12px;border-bottom:1px solid #eee;text-align:center;">
                <span style="color:{color};font-weight:700;font-size:1.2rem;">{score}</span>
            </td>
            <td style="padding:12px;border-bottom:1px solid #eee;text-align:center;">
                <span style="background:{color};color:white;padding:3px 10px;
                      border-radius:12px;font-size:0.8rem;">{rec}</span>
            </td>
            <td style="padding:12px;border-bottom:1px solid #eee;font-size:0.85rem;">
                ✅ {matched}<br>❌ {missing}
            </td>
            <td style="padding:12px;border-bottom:1px solid #eee;">
                <a href="{job_url}" style="background:#7c83ff;color:white;
                   padding:6px 14px;border-radius:6px;text-decoration:none;
                   font-size:0.85rem;">View Job</a>
            </td>
        </tr>
        """

    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:20px;">
        <div style="background:linear-gradient(135deg,#1e2130,#252840);
                    border-radius:12px;padding:24px;margin-bottom:24px;">
            <h1 style="color:#ffffff;margin:0;">🤖 Job Application Agent</h1>
            <p style="color:#9098b1;margin:8px 0 0;">
                Daily digest — {len(jobs)} job(s) scored above your auto-apply threshold
            </p>
        </div>
        <table style="width:100%;border-collapse:collapse;background:#fff;
                      border-radius:12px;overflow:hidden;
                      box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background:#f8f9fa;">
                    <th style="padding:12px;text-align:left;color:#444;">Job</th>
                    <th style="padding:12px;text-align:center;color:#444;">Score</th>
                    <th style="padding:12px;text-align:center;color:#444;">Decision</th>
                    <th style="padding:12px;text-align:left;color:#444;">Skills</th>
                    <th style="padding:12px;text-align:left;color:#444;">Link</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <div style="margin-top:24px;padding:16px;background:#f8f9fa;
                    border-radius:8px;text-align:center;">
            <p style="color:#666;font-size:0.85rem;margin:0;">
                Sent by your Job Application Agent ·
                Update application status in your
                <a href="http://localhost:8501" style="color:#7c83ff;">dashboard</a>
            </p>
        </div>
    </body>
    </html>
    """