import re
import urllib.parse
from typing import List
from .base_strategy import BaseJobStrategy, RawJobData

class AmazonStrategy(BaseJobStrategy):
    name: str = "Amazon Jobs"

    def can_handle(self, parsed_url: urllib.parse.ParseResult) -> bool:
        host = (parsed_url.hostname or "").lower()
        return host == "amazon.jobs" or host.endswith(".amazon.jobs")

    def extract(self, page, url: str) -> RawJobData:
        data = RawJobData(url=url, source="Amazon Jobs", company="Amazon")

        # Extract Job ID from URL (e.g. /jobs/10565307/...)
        id_match = re.search(r'/jobs/(\d+)', url)
        if id_match:
            data.job_id = id_match.group(1)

        # Wait for main content or heading
        try:
            page.wait_for_selector("h1, .job-title, #job-detail", timeout=12000)
        except Exception:
            pass

        # 1. Job Title
        title_selectors = [
            "h1.title", "h1.job-title", "h1.title-heading",
            "h1", "h2.job-title", "[data-test-id='job-title']"
        ]
        for sel in title_selectors:
            el = page.query_selector(sel)
            if el:
                txt = el.inner_text().strip()
                if txt and not any(skip in txt.lower() for skip in ["find jobs", "search", "amazon"]):
                    data.title = txt
                    break
        if not data.title:
            page_title = page.title() or ""
            data.title = re.sub(r'\s*\|\s*Amazon\.jobs.*', '', page_title, flags=re.IGNORECASE).strip()

        # 2. Location
        loc_selectors = [
            ".location-text", ".job-location", "[data-test-id='location']",
            ".locations-container", ".association-badge--location",
            "p.location", "div.location"
        ]
        for sel in loc_selectors:
            el = page.query_selector(sel)
            if el:
                txt = el.inner_text().strip()
                if txt:
                    data.location = txt.replace("\n", ", ")
                    break

        # 3. Employment Type & Experience
        badge_els = page.query_selector_all(".association-badge, .badge, .meta-item")
        for b in badge_els:
            txt = b.inner_text().strip()
            if any(term in txt.lower() for term in ["full-time", "part-time", "contract", "intern"]):
                data.employment_type = txt
            elif "year" in txt.lower() or "level" in txt.lower():
                data.experience = txt

        # 4. Extract Description Container & Text
        body_el = page.query_selector("#job-detail-body, .job-detail, .description, main")
        full_text = body_el.inner_text().strip() if body_el else (page.inner_text("body") or "")

        data.description = full_text

        # 5. Extract structured sections (Basic Qualifications vs Preferred Qualifications vs Responsibilities)
        # Often formatted with headings like:
        # "DESCRIPTION", "Key job responsibilities", "BASIC QUALIFICATIONS", "PREFERRED QUALIFICATIONS"
        basic_quals: List[str] = []
        pref_quals: List[str] = []
        responsibilities: List[str] = []

        # Try section-based regex parsing on the full text
        sec_pattern = re.compile(
            r'(?:^|\n)\s*(DESCRIPTION|KEY JOB RESPONSIBILITIES|RESPONSIBILITIES|BASIC QUALIFICATIONS|PREFERRED QUALIFICATIONS)\s*(?:\n|:)',
            re.IGNORECASE
        )
        splits = sec_pattern.split(full_text)
        if len(splits) > 1:
            # We have captured section headers and contents
            i = 1
            while i < len(splits):
                header = splits[i].strip().upper()
                content = splits[i+1].strip() if i+1 < len(splits) else ""
                data.raw_sections[header] = content

                if "BASIC" in header:
                    data.basic_qualifications_text = content
                    basic_quals.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                elif "PREFERRED" in header:
                    data.preferred_qualifications_text = content
                    pref_quals.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                elif "RESPONSIBIL" in header:
                    responsibilities.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                i += 2

        # Fallback element selectors for qualifications
        if not data.basic_qualifications_text:
            bq_el = page.query_selector("[data-test-id='basic-qualifications'], #basic-qualifications")
            if bq_el:
                data.basic_qualifications_text = bq_el.inner_text().strip()
                basic_quals.extend([li.inner_text().strip() for li in bq_el.query_selector_all("li")])

        if not data.preferred_qualifications_text:
            pq_el = page.query_selector("[data-test-id='preferred-qualifications'], #preferred-qualifications")
            if pq_el:
                data.preferred_qualifications_text = pq_el.inner_text().strip()
                pref_quals.extend([li.inner_text().strip() for li in pq_el.query_selector_all("li")])

        data.qualifications = basic_quals + pref_quals
        data.responsibilities = responsibilities

        # Unavailable fields check
        for field_name, val in [("location", data.location), ("experience", data.experience),
                                ("employment_type", data.employment_type), ("responsibilities", data.responsibilities)]:
            if not val:
                data.unavailable_fields.append(field_name)

        if not data.title or not data.description:
            data.status = "partial" if (data.title or data.description) else "error"
            if data.status == "error":
                data.error_message = "Failed to extract core job title or description from Amazon Jobs posting."

        return data

