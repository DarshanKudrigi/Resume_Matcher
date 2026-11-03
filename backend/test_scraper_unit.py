import unittest
import urllib.parse
from pathlib import Path
import sys

AGENT_DIR = Path(__file__).resolve().parent.parent / "job-application-agent"
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from scraper.url_scraper import validate_and_sanitize_url, IndividualJobScraper, RawJobData
from scraper.strategies import AmazonStrategy, MicrosoftStrategy, LeverStrategy, GenericStrategy
from app.services.job_scraper_service import classify_skills_from_job

class TestIndividualJobScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = IndividualJobScraper(headless=True)

    def test_url_validation_valid(self):
        valid_urls = [
            "https://www.amazon.jobs/en/jobs/10565307/snr-manager",
            "https://jobs.lever.co/drivetrain/d7808cbe-0c2f-47f0-9261-f10f6cfea9aa",
            "https://apply.careers.microsoft.com/careers?query=Software&pid=1970393557026326"
        ]
        for u in valid_urls:
            parsed = validate_and_sanitize_url(u)
            self.assertIn(parsed.scheme, ("http", "https"))
            self.assertTrue(bool(parsed.hostname))

    def test_url_validation_blocked_ssrf(self):
        blocked_urls = [
            "http://localhost:8000/secret",
            "http://127.0.0.1:5000",
            "http://admin:pass@example.com/job",
            "ftp://example.com/job",
            "http://169.254.169.254/latest/meta-data/"
        ]
        for u in blocked_urls:
            with self.assertRaises(ValueError):
                validate_and_sanitize_url(u)

    def test_strategy_selection(self):
        cases = [
            ("https://www.amazon.jobs/en/jobs/123", AmazonStrategy),
            ("https://apply.careers.microsoft.com/careers?pid=123", MicrosoftStrategy),
            ("https://jobs.lever.co/company/abc", LeverStrategy),
            ("https://example.com/careers/job-123", GenericStrategy)
        ]
        for url, expected_cls in cases:
            parsed = urllib.parse.urlparse(url)
            strat = self.scraper.select_strategy(parsed)
            self.assertIsInstance(strat, expected_cls, f"URL {url} mapped to {type(strat)} instead of {expected_cls}")

    def test_skill_classification_explicit_sections(self):
        raw_job = RawJobData(
            basic_qualifications_text="Proficiency in Python, SQL, and Docker is required. Must have experience with React.",
            preferred_qualifications_text="Experience with Kubernetes, AWS, and GraphQL is a plus.",
            description="Full text here"
        )
        req, pref, unclass = classify_skills_from_job(raw_job)
        self.assertIn("Python", req)
        self.assertIn("SQL", req)
        self.assertIn("Docker", req)
        self.assertIn("React", req)
        self.assertIn("Kubernetes", pref)
        self.assertIn("AWS", pref)
        self.assertIn("GraphQL", pref)

    def test_skill_classification_unstructured_text(self):
        raw_job = RawJobData(
            description="""
            We are looking for a Software Engineer.
            Candidate must have strong experience with Python and JavaScript.
            Knowledge of Docker and AWS is preferred.
            We use Git and Agile workflows daily.
            """
        )
        req, pref, unclass = classify_skills_from_job(raw_job)
        self.assertIn("Python", req)
        self.assertIn("JavaScript", req)
        self.assertIn("Docker", pref)
        self.assertIn("AWS", pref)
        self.assertIn("Git", unclass)

if __name__ == "__main__":
    unittest.main()

