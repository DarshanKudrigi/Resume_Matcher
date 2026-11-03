import sys
import os
import unittest
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import HTTPException
from app.schemas.job import JobParseRequest
from app.routers.jobs import parse_job_description

class TestJobParseRouterDirect(unittest.TestCase):
    def test_parse_text_job(self):
        req = JobParseRequest(
            text="""
            Senior Frontend Engineer
            Requirements:
            - Must have solid experience with TypeScript, React, and Redux.
            - Strong knowledge of HTML and CSS.
            Preferred Qualifications:
            - Familiarity with Next.js, GraphQL, and AWS.
            Responsibilities:
            - Build accessible web applications.
            """
        )
        res = asyncio.run(parse_job_description(req, db=None))
        self.assertEqual(res.status, "success")
        self.assertEqual(res.title, "Senior Frontend Engineer")
        self.assertIn("React", res.requiredSkills)
        self.assertIn("TypeScript", res.requiredSkills)
        self.assertIn("GraphQL", res.preferredSkills)
        self.assertIn("AWS", res.preferredSkills)

    def test_parse_invalid_url_protocol(self):
        req = JobParseRequest(url="ftp://example.com/job")
        with self.assertRaises(HTTPException) as cm:
            asyncio.run(parse_job_description(req, db=None))
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Invalid URL protocol", cm.exception.detail)

    def test_parse_blocked_loopback_url(self):
        req = JobParseRequest(url="http://localhost:8000/internal")
        with self.assertRaises(HTTPException) as cm:
            asyncio.run(parse_job_description(req, db=None))
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("loopback", cm.exception.detail.lower())

    def test_parse_empty_payload(self):
        req = JobParseRequest()
        with self.assertRaises(HTTPException) as cm:
            asyncio.run(parse_job_description(req, db=None))
        self.assertEqual(cm.exception.status_code, 400)

if __name__ == "__main__":
    unittest.main()
