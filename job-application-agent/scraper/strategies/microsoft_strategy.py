import re
import urllib.parse
from typing import List
from .base_strategy import BaseJobStrategy, RawJobData

class MicrosoftStrategy(BaseJobStrategy):
    name: str = "Microsoft Careers"

    def can_handle(self, parsed_url: urllib.parse.ParseResult) -> bool:
        host = (parsed_url.hostname or "").lower()
        return "careers.microsoft.com" in host

    def extract(self, page, url: str) -> RawJobData:
        data = RawJobData(url=url, source="Microsoft Careers", company="Microsoft")
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)

        pid = params.get("pid", [None])[0] or params.get("jobId", [None])[0] or params.get("job_id", [None])[0]
        
        # Check if URL path has job ID (e.g., /job/1970393557026326 or /us/en/job/...)
        if not pid:
            path_match = re.search(r'/job(?:s)?/([0-9a-zA-Z_\-]+)', parsed.path)
            if path_match:
                pid = path_match.group(1)

        # If it is purely a search query URL without any job ID or pid
        if not pid and ("query=" in parsed.query or "/search" in parsed.path):
            data.status = "error"
            data.error_message = (
                "The provided Microsoft Careers URL is a general search results page with no specific job ID (pid). "
                "Please provide a specific job posting URL containing a job ID or 'pid' parameter."
            )
            return data

        data.job_id = pid or ""

        # Wait for the job detail container to load
        try:
            # If pid is specified, wait for elements containing job details
            page.wait_for_selector(
                "[data-ph-id], .job-description, .job-details, [role='main'], h1, .ph-job-title",
                timeout=15000
            )
        except Exception:
            pass

        # If there are search results on the page, verify that the pid matches the loaded job
        # Or look for job card matching the pid and click it if necessary to open details
        if pid:
            try:
                card_for_pid = page.query_selector(f"[data-job-id='{pid}'], a[href*='{pid}'], [id*='{pid}']")
                if card_for_pid:
                    # If this card isn't already active/expanded, clicking it might reveal the detail
                    try:
                        card_for_pid.click(timeout=2000)
                        page.wait_for_timeout(1000)
                    except Exception:
                        pass
            except Exception:
                pass

        # 1. Job Title: check page.title() first since Microsoft sets the specific role title in document.title
        page_title = (page.title() or "").strip()
        clean_page_title = re.sub(r'\s*\|\s*Microsoft\s*(?:Careers)?.*', '', page_title, flags=re.IGNORECASE).strip()
        if clean_page_title and clean_page_title.lower() not in ("jobs", "careers", "search results", "microsoft careers"):
            data.title = clean_page_title

        # Check headings if page title was generic
        if not data.title:
            title_selectors = [
                "h2[class*='jobTitle']", "h2",
                "[data-ph-id*='job-title']",
                "h1.job-title", "h1[class*='jobTitle']", "h1.ph-job-title"
            ]
            for sel in title_selectors:
                el = page.query_selector(sel)
                if el:
                    txt = el.inner_text().strip()
                    if txt and txt.lower() not in ("jobs", "search results", "careers at microsoft", "get personalized job recommendations"):
                        data.title = txt
                        break

        # 2. Location & Employment Info
        loc_selectors = [
            "[data-ph-id*='location']", ".job-location", "[class*='jobLocation']",
            "[data-ph-at-id='job-location-text']", ".location"
        ]
        for sel in loc_selectors:
            el = page.query_selector(sel)
            if el:
                txt = el.inner_text().strip()
                if txt and "location" not in txt.lower():
                    data.location = txt.replace("\n", ", ")
                    break

        # 3. Full Job Description text: query body directly to ensure complete text is captured
        body_text = page.inner_text("body") or ""
        data.description = body_text

        # 4. Check whether this is still just an unselected search page
        if pid and pid not in body_text and pid not in page.content():
            data.warnings.append(f"Specified job ID '{pid}' could not be definitively verified in page content.")

        # 5. Extract Responsibilities, Minimum/Required Qualifications, Preferred Qualifications
        # Microsoft structure often has:
        # "Responsibilities", "Qualifications", "Required/Minimum Qualifications", "Additional or Preferred Qualifications"
        resp_list: List[str] = []
        quals_list: List[str] = []

        sec_pattern = re.compile(
            r'(?:^|\n)\s*(RESPONSIBILITIES|QUALIFICATIONS|REQUIRED QUALIFICATIONS|MINIMUM QUALIFICATIONS|PREFERRED QUALIFICATIONS|DESIRED QUALIFICATIONS)\s*(?:\n|:)',
            re.IGNORECASE
        )
        splits = sec_pattern.split(body_text)
        if len(splits) > 1:
            i = 1
            while i < len(splits):
                header = splits[i].strip().upper()
                content = splits[i+1].strip() if i+1 < len(splits) else ""
                data.raw_sections[header] = content

                if any(k in header for k in ["REQUIRED", "MINIMUM"]):
                    data.basic_qualifications_text += ("\n" + content)
                    quals_list.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                elif any(k in header for k in ["PREFERRED", "DESIRED", "ADDITIONAL"]):
                    data.preferred_qualifications_text += ("\n" + content)
                    quals_list.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                elif "RESPONSIBIL" in header:
                    resp_list.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                elif "QUALIFICATION" in header:
                    quals_list.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                    if not data.basic_qualifications_text:
                        data.basic_qualifications_text = content
                i += 2

        data.responsibilities = resp_list
        data.qualifications = quals_list

        # Mark unavailable fields
        for field_name, val in [("location", data.location), ("experience", data.experience),
                                ("employment_type", data.employment_type), ("responsibilities", data.responsibilities)]:
            if not val:
                data.unavailable_fields.append(field_name)

        if not data.title or len(data.description) < 50:
            data.status = "error"
            data.error_message = (
                f"Could not resolve the specific Microsoft job details for ID '{pid or 'unknown'}'. "
                "The posting may be expired or the search view did not render the job container."
            )
        elif not data.qualifications and not data.responsibilities:
            data.status = "partial"

        return data
