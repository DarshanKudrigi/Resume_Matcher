import re
import urllib.parse
from typing import List
from .base_strategy import BaseJobStrategy, RawJobData

class NaukriStrategy(BaseJobStrategy):
    name: str = "Naukri"

    def can_handle(self, parsed_url: urllib.parse.ParseResult) -> bool:
        host = (parsed_url.hostname or "").lower()
        return "naukri.com" in host

    def extract(self, page, url: str) -> RawJobData:
        data = RawJobData(url=url, source="Naukri", company="Naukri Employer")
        parsed = urllib.parse.urlparse(url)

        # Extract job ID if available in path (e.g. /job-listings-python-dev-12345)
        id_match = re.search(r'-(\d+)(?:\?|$)', parsed.path)
        if id_match:
            data.job_id = id_match.group(1)

        try:
            page.wait_for_selector(
                ".styles_JDC__dang-inner-html__h0K4t, .job-desc, #job-desc, h1, .styles_jpc__title__",
                timeout=15000
            )
        except Exception:
            pass

        # Dismiss any close button
        try:
            close_btn = page.query_selector("button.close-btn, .crossIcon, [aria-label='Close']")
            if close_btn:
                close_btn.click(timeout=1500)
                page.wait_for_timeout(400)
        except Exception:
            pass

        # 1. Title
        title_selectors = [
            ".styles_jpc__title__",
            "h1.title",
            "h1",
            ".title",
            ".jd-header-title"
        ]
        for sel in title_selectors:
            el = page.query_selector(sel)
            if el:
                txt = el.inner_text().strip()
                if txt and not any(skip in txt.lower() for skip in ["search jobs", "naukri", "log in"]):
                    data.title = txt
                    break

        if not data.title:
            page_title = page.title() or ""
            data.title = re.sub(r'\s*-\s*Naukri\.com.*', '', page_title, flags=re.IGNORECASE).strip()

        # 2. Company
        comp_selectors = [
            ".styles_jpc__header__comp-name",
            ".comp-name",
            ".company-name",
            "a.pad-rt-8"
        ]
        for sel in comp_selectors:
            el = page.query_selector(sel)
            if el:
                txt = el.inner_text().strip()
                if txt and "naukri" not in txt.lower():
                    data.company = txt
                    break

        # 3. Location & Experience
        loc_el = page.query_selector(".styles_jpc__header__location, .locWdth, .location")
        if loc_el:
            data.location = loc_el.inner_text().strip()

        exp_el = page.query_selector(".styles_jpc__header__experience, .exp, .experience")
        if exp_el:
            data.experience = exp_el.inner_text().strip()

        # 4. Job Description
        desc_selectors = [
            ".styles_JDC__dang-inner-html__h0K4t",
            ".job-desc",
            "#job-desc",
            ".dang-inner-html",
            "[class*='dang-inner-html']"
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

        # 5. Extract structured sections
        sec_pattern = re.compile(
            r'(?:^|\n)\s*(ROLE & RESPONSIBILITIES|RESPONSIBILITIES|DESIRED CANDIDATE PROFILE|KEY SKILLS|REQUIREMENTS|QUALIFICATIONS|EDUCATION)\s*(?:\n|:)',
            re.IGNORECASE
        )
        splits = sec_pattern.split(desc_text)
        if len(splits) > 1:
            i = 1
            while i < len(splits):
                header = splits[i].strip().upper()
                content = splits[i+1].strip() if i+1 < len(splits) else ""
                bullets = [b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")]

                if any(k in header for k in ["DESIRED", "REQUIREMENT", "QUALIFICATION", "KEY SKILLS"]):
                    data.basic_qualifications_text += ("\n" + content)
                    data.qualifications.extend(bullets if bullets else [content])
                elif any(k in header for k in ["RESPONSIBIL", "ROLE"]):
                    data.responsibilities.extend(bullets if bullets else [content])
                i += 2

        # Key skills tags if rendered by Naukri as pills
        skill_tags = [el.inner_text().strip() for el in page.query_selector_all(".styles_key-skill__list a, .key-skill a") if el.inner_text().strip()]
        if skill_tags:
            data.basic_qualifications_text += "\nKey Skills: " + ", ".join(skill_tags)

        for field_name, val in [("location", data.location), ("experience", data.experience),
                                ("employment_type", data.employment_type), ("responsibilities", data.responsibilities)]:
            if not val:
                data.unavailable_fields.append(field_name)

        if not data.title or not data.description or len(data.description) < 40:
            data.status = "error"
            data.error_message = "Could not extract job details from Naukri. Posting may have expired or blocked."
        elif not data.responsibilities and not data.qualifications:
            data.status = "partial"

        return data

