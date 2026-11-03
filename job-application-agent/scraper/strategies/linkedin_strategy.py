import re
import urllib.parse
from typing import List
from .base_strategy import BaseJobStrategy, RawJobData

class LinkedInStrategy(BaseJobStrategy):
    name: str = "LinkedIn"

    def can_handle(self, parsed_url: urllib.parse.ParseResult) -> bool:
        host = (parsed_url.hostname or "").lower()
        return "linkedin.com" in host

    def extract(self, page, url: str) -> RawJobData:
        data = RawJobData(url=url, source="LinkedIn")
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)

        # 1. Resolve Job ID from query parameter or path
        # Examples:
        # - ?currentJobId=4454538326
        # - /jobs/view/4454538326/
        # - /jobs/view/software-engineer-intern-at-stripe-4454538326
        job_id = params.get("currentJobId", [None])[0] or params.get("jobId", [None])[0]
        if not job_id:
            path_match = re.search(r'/jobs/view/(?:[a-zA-Z0-9_\-]+-)?(\d+)', parsed.path)
            if path_match:
                job_id = path_match.group(1)

        # If a specific job ID was resolved and current URL is an internal authenticated search path
        # navigate directly to the public job view to avoid the login wall
        if job_id and ("search-results" in parsed.path or "collections" in parsed.path or not parsed.path.startswith("/jobs/view")):
            public_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
            try:
                page.goto(public_url, timeout=30000, wait_until="domcontentloaded")
            except Exception:
                pass
        
        data.job_id = job_id or ""

        # Check if redirected to authwall or login
        current_url = page.url or ""
        if "/authwall" in current_url or "/login" in current_url:
            data.status = "error"
            data.error_message = (
                "LinkedIn requires login or redirected to an authentication wall. "
                "Try providing the direct public job view link (https://www.linkedin.com/jobs/view/<job_id>/)."
            )
            return data

        # Dismiss any popups or modals
        try:
            close_btn = page.query_selector("button[aria-label='Dismiss'], button.modal__dismiss, .artdeco-modal__dismiss")
            if close_btn:
                close_btn.click(timeout=2000)
                page.wait_for_timeout(500)
        except Exception:
            pass

        # 2. Extract Job Title
        title_selectors = [
            ".top-card-layout__title",
            ".topcard__title",
            "h1.top-card-layout__title",
            "h1",
            "h2.top-card-layout__title"
        ]
        for sel in title_selectors:
            el = page.query_selector(sel)
            if el:
                txt = el.inner_text().strip()
                if txt and not any(skip in txt.lower() for skip in ["sign in", "join now", "linkedin"]):
                    data.title = txt
                    break

        # Fallback to document title
        if not data.title:
            doc_title = page.title() or ""
            # e.g. "Software Engineer, Intern at Stripe | LinkedIn"
            data.title = re.sub(r'\s*\|\s*LinkedIn.*', '', doc_title, flags=re.IGNORECASE)
            data.title = re.sub(r'\s+at\s+.*', '', data.title, flags=re.IGNORECASE).strip()

        # 3. Extract Company Name
        comp_selectors = [
            ".topcard__org-name-link",
            ".topcard__flavor--black-link",
            "a[data-tracking-control-name*='topcard-org-name']",
            ".top-card-layout__first-sub-line a",
            ".topcard__flavor"
        ]
        for sel in comp_selectors:
            el = page.query_selector(sel)
            if el:
                txt = el.inner_text().strip()
                if txt and "linkedin" not in txt.lower():
                    data.company = txt
                    break

        if not data.company and " at " in (page.title() or ""):
            # Extract from "Role at Company | LinkedIn"
            m = re.search(r'\sat\s+([^|•]+)', page.title())
            if m:
                data.company = m.group(1).strip()

        # 4. Extract Location
        loc_selectors = [
            ".topcard__flavor--bullet",
            ".top-card-layout__second-sub-line span",
            ".top-card-layout__first-sub-line span.topcard__flavor--bullet"
        ]
        for sel in loc_selectors:
            el = page.query_selector(sel)
            if el:
                txt = el.inner_text().strip()
                if txt and txt != data.company:
                    data.location = txt
                    break

        # 5. Extract Job Description
        desc_selectors = [
            ".show-more-less-html__markup",
            ".description__text",
            ".decorated-job-posting__details",
            "[data-job-description]"
        ]
        desc_text = ""
        for sel in desc_selectors:
            el = page.query_selector(sel)
            if el:
                txt = el.inner_text().strip()
                if len(txt) > len(desc_text):
                    desc_text = txt

        if not desc_text:
            desc_text = page.inner_text("body") or ""

        data.description = desc_text

        # Extract Employment Type if present in bottom badges
        emp_match = re.search(r'Employment type\s*\n\s*([^\n]+)', desc_text, re.IGNORECASE)
        if emp_match:
            data.employment_type = emp_match.group(1).strip()
        else:
            if "intern" in (data.title or "").lower():
                data.employment_type = "Internship"

        # 6. Extract structured sections (Responsibilities & Qualifications)
        resp_list: List[str] = []
        quals_list: List[str] = []

        sec_pattern = re.compile(
            r'(?:^|\n)\s*(MINIMUM REQUIREMENTS|REQUIRED QUALIFICATIONS|MINIMUM QUALIFICATIONS|PREFERRED QUALIFICATIONS|RESPONSIBILITIES|WHAT YOU\'LL DO|WHAT YOU WILL DO|YOU WILL|WHO YOU ARE|YOU HAVE|NICE TO HAVE|BONUS|QUALIFICATIONS)\s*(?:\n|:)',
            re.IGNORECASE
        )
        splits = sec_pattern.split(desc_text)
        if len(splits) > 1:
            i = 1
            while i < len(splits):
                header = splits[i].strip().upper()
                content = splits[i+1].strip() if i+1 < len(splits) else ""
                data.raw_sections[header] = content

                bullets = [b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")]

                if any(k in header for k in ["PREFERRED", "NICE", "BONUS"]):
                    data.preferred_qualifications_text += ("\n" + content)
                    quals_list.extend(bullets if bullets else [content])
                elif any(k in header for k in ["MINIMUM", "REQUIREMENT", "REQUIRED", "QUALIFICATION", "YOU HAVE"]):
                    data.basic_qualifications_text += ("\n" + content)
                    quals_list.extend(bullets if bullets else [content])
                elif any(k in header for k in ["YOU WILL", "RESPONSIBIL", "WHAT YOU"]):
                    resp_list.extend(bullets if bullets else [content])
                i += 2

        data.responsibilities = resp_list
        data.qualifications = quals_list

        for field_name, val in [("location", data.location), ("experience", data.experience),
                                ("employment_type", data.employment_type), ("responsibilities", data.responsibilities)]:
            if not val:
                data.unavailable_fields.append(field_name)

        if not data.title or not data.description or len(data.description) < 50:
            data.status = "error"
            data.error_message = (
                f"Could not extract LinkedIn job details for ID '{job_id or 'unknown'}'. "
                "The posting may require a login or has been closed."
            )
        elif not data.responsibilities and not data.qualifications:
            data.status = "partial"

        return data
