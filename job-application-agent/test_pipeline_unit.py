"""Unit and integration test suite for the Job Application Agent pipeline."""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from tracker.models import Job
from config import GROQ_MODEL, MATCH_THRESHOLD
from matcher.resume_matcher import (
    score_job,
    filter_jobs,
    _clean_json_response,
    _parse_and_validate_scoring,
    get_client,
)
from tracker.sheets_tracker import log_jobs, clear_sheet, HEADERS
from notifier.email_notifier import send_daily_digest


class TestJobModel(unittest.TestCase):
    def test_stable_id_generation(self):
        job1 = Job(
            title="AI Engineer",
            company="Google",
            location="Bengaluru",
            url="https://www.linkedin.com/jobs/view/12345?refId=abc&trackingId=xyz",
            description="ML engineer",
            source="linkedin",
            scraped_at=datetime.now().isoformat(),
        )
        job2 = Job(
            title="AI Engineer",
            company="Google",
            location="Bengaluru",
            url="https://www.linkedin.com/jobs/view/12345?differentTracking=999",
            description="ML engineer",
            source="linkedin",
            scraped_at=datetime.now().isoformat(),
        )
        # Normalized URLs should produce the same stable ID
        self.assertEqual(job1.id, job2.id)

    def test_default_unscored_state(self):
        job = Job(
            title="Dev", company="Corp", location="Blr",
            url="https://example.com/job", description="...",
            source="test", scraped_at=datetime.now().isoformat()
        )
        self.assertIsNone(job.match_score)
        self.assertFalse(job.scored)
        self.assertIsNone(job.scoring_error)


class TestResumeMatcher(unittest.TestCase):
    def test_clean_json_response(self):
        fenced = '```json\n{"score": 0.85, "recommendation": "apply"}\n```'
        cleaned = _clean_json_response(fenced)
        self.assertEqual(cleaned, '{"score": 0.85, "recommendation": "apply"}')

    def test_parse_and_validate(self):
        raw = '{"score": 85.0, "matched_skills": ["Python"], "missing_skills": ["Go"], "recommendation": "apply", "experience_required": 1}'
        parsed = _parse_and_validate_scoring(raw)
        self.assertAlmostEqual(parsed["score"], 0.85)
        self.assertEqual(parsed["recommendation"], "apply")
        self.assertEqual(parsed["experience_required"], 1)

    def test_simulated_api_failure_does_not_score_zero(self):
        job = Job(
            title="ML Engineer", company="Corp", location="Blr",
            url="https://example.com/ml", description="...",
            source="test", scraped_at=datetime.now().isoformat()
        )
        with patch("matcher.resume_matcher.get_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.chat.completions.create.side_effect = Exception("Simulated connection timeout")

            scored_job = score_job(job, "sample resume", max_retries=1)
            self.assertFalse(scored_job.scored)
            self.assertIsNone(scored_job.match_score)
            self.assertIsNotNone(scored_job.scoring_error)

            # filter_jobs must exclude it
            filtered = filter_jobs([scored_job], threshold=MATCH_THRESHOLD)
            self.assertEqual(len(filtered), 0)

    def test_experience_filtering(self):
        high_exp_job = Job(
            title="Senior Director AI", company="Corp", location="Blr",
            url="https://example.com/senior", description="...",
            source="test", scraped_at=datetime.now().isoformat(),
            match_score=0.95, scored=True,
            match_meta={"experience_required": 8, "recommendation": "apply"}
        )
        fresh_job = Job(
            title="Junior AI", company="Corp", location="Blr",
            url="https://example.com/junior", description="...",
            source="test", scraped_at=datetime.now().isoformat(),
            match_score=0.80, scored=True,
            match_meta={"experience_required": 1, "recommendation": "apply"}
        )
        filtered = filter_jobs([high_exp_job, fresh_job], threshold=0.65)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "Junior AI")


class TestSheetsTracker(unittest.TestCase):
    def test_clear_sheet_without_confirm_is_aborted(self):
        mock_sheet = MagicMock()
        with patch("tracker.sheets_tracker.get_sheet", return_value=mock_sheet):
            clear_sheet(confirm=False)
            self.assertFalse(mock_sheet.clear.called)

    def test_log_jobs_deduplication(self):
        mock_sheet = MagicMock()
        mock_sheet.row_values.return_value = HEADERS
        mock_sheet.col_values.side_effect = lambda col: ["ID", "existing123"] if col == 1 else (["URL", "https://example.com/job1"] if col == 5 else [])

        dup_job = Job(
            title="AI Dev", company="A", location="B",
            url="https://example.com/job1", description="...",
            source="test", scraped_at=datetime.now().isoformat(),
            match_score=0.90, scored=True, match_meta={"recommendation": "apply"}
        )
        dup_job.id = "existing123"

        new_job = Job(
            title="ML Dev", company="B", location="C",
            url="https://example.com/job2", description="...",
            source="test", scraped_at=datetime.now().isoformat(),
            match_score=0.88, scored=True, match_meta={"recommendation": "apply"}
        )
        new_job.id = "new4567890"

        with patch("tracker.sheets_tracker.get_sheet", return_value=mock_sheet):
            log_jobs([dup_job, new_job], min_threshold=0.65)
            self.assertTrue(mock_sheet.append_rows.called)
            rows = mock_sheet.append_rows.call_args[0][0]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "new4567890")


class TestEmailNotifier(unittest.TestCase):
    def test_duplicate_notification_skipped(self):
        job = Job(
            title="AI Dev", company="A", location="B",
            url="https://example.com/job1", description="...",
            source="test", scraped_at=datetime.now().isoformat(),
            match_score=0.90, scored=True, match_meta={"recommendation": "apply"}
        )
        with patch("notifier.email_notifier._get_notified_job_ids", return_value={job.id}), \
             patch("resend.Emails.send") as mock_send:
            send_daily_digest([job])
            self.assertFalse(mock_send.called)


if __name__ == "__main__":
    unittest.main()
