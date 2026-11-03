import json
import re
import urllib.parse
from typing import List, Dict, Any
from .base_strategy import BaseJobStrategy, RawJobData

class GenericStrategy(BaseJobStrategy):
    name: str = "Generic Job Portal"

    def can_handle(self, parsed_url: urllib.parse.ParseResult) -> bool:
        # Fallback for all other domains
        return True

    def extract(self, page, url: str) -> RawJobData:
        data = RawJobData(url=url, source="Web")
        parsed = urllib.parse.urlparse(url)
        data.source = parsed.hostname or "Web"

        try:
            page.wait_for_load_state("domcontentloaded", timeout=12000)
        except Exception:
            pass

        # 1. PRIORITY 1: JSON-LD Structured Data (schema.org/JobPosting)
        json_ld_scripts = page.query_selector_all("script[type='application/ld+json']")
        job_schema: Dict[str, Any] = {}
        for s in json_ld_scripts:
            try:
                raw_json = s.inner_text().strip()
                if not raw_json:
                    continue
                parsed_json = json.loads(raw_json)
                if isinstance(parsed_json, list):
                    candidates = parsed_json
                elif isinstance(parsed_json, dict) and "@graph" in parsed_json:
                    candidates = parsed_json["@graph"]
                else:
                    candidates = [parsed_json]

                for item in candidates:
                    if isinstance(item, dict) and str(item.get("@type", "")).lower() in ("jobposting", "job_posting"):
                        job_schema = item
                        break
                if job_schema:
                    break
            except Exception:
                continue

        if job_schema:
            data.title = str(job_schema.get("title", "")).strip()
            
            hiring_org = job_schema.get("hiringOrganization")
            if isinstance(hiring_org, dict):
                data.company = str(hiring_org.get("name", "")).strip()
            elif isinstance(hiring_org, str):
                data.company = hiring_org.strip()

            job_loc = job_schema.get("jobLocation")
            if isinstance(job_loc, dict):
                addr = job_loc.get("address", {})
                if isinstance(addr, dict):
                    loc_parts = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
                    data.location = ", ".join([str(p) for p in loc_parts if p])
                elif isinstance(addr, str):
                    data.location = addr
            elif isinstance(job_loc, list) and len(job_loc) > 0:
                first_loc = job_loc[0]
                if isinstance(first_loc, dict):
                    addr = first_loc.get("address", {})
                    if isinstance(addr, dict):
                        data.location = str(addr.get("addressLocality") or "")

            raw_desc = str(job_schema.get("description", "")).strip()
            if raw_desc:
                # Strip HTML tags from JSON-LD description
                clean_desc = re.sub(r'<[^>]+>', '\n', raw_desc)
                data.description = re.sub(r'\n{3,}', '\n\n', clean_desc).strip()

            emp_type = job_schema.get("employmentType")
            if isinstance(emp_type, str):
                data.employment_type = emp_type
            elif isinstance(emp_type, list):
                data.employment_type = ", ".join([str(e) for e in emp_type])

        # 2. PRIORITY 2: Open Graph Metadata Fallbacks
        if not data.title:
            og_title = page.query_selector("meta[property='og:title'], meta[name='twitter:title']")
            if og_title:
                data.title = (og_title.get_attribute("content") or "").strip()

        if not data.company:
            og_site = page.query_selector("meta[property='og:site_name'], meta[name='author']")
            if og_site:
                data.company = (og_site.get_attribute("content") or "").strip()
            else:
                # Use hostname as company fallback
                domain = (parsed.hostname or "").replace("www.", "")
                data.company = domain.split(".")[0].capitalize()

        if not data.description:
            og_desc = page.query_selector("meta[property='og:description'], meta[name='description']")
            if og_desc:
                data.description = (og_desc.get_attribute("content") or "").strip()

        # 3. PRIORITY 3: Semantic HTML Fallback
        if not data.title:
            h1 = page.query_selector("h1")
            if h1:
                txt = h1.inner_text().strip()
                if len(txt) > 3 and "\n" not in txt:
                    data.title = txt

        if not data.description or len(data.description) < 100:
            containers = [
                "[class*='job-description']", "[class*='jobDescription']",
                "[id*='job-description']", "[id*='jobDescription']",
                "article", "main", "[role='main']", ".content"
            ]
            for sel in containers:
                el = page.query_selector(sel)
                if el:
                    txt = el.inner_text().strip()
                    if len(txt) > len(data.description):
                        data.description = txt

        # 4. Extract sections (Requirements / Qualifications / Responsibilities)
        if data.description:
            sec_pattern = re.compile(
                r'(?:^|\n)\s*(RESPONSIBILITIES|WHAT YOU\'LL DO|REQUIREMENTS|QUALIFICATIONS|MINIMUM QUALIFICATIONS|PREFERRED QUALIFICATIONS|NICE TO HAVE|MUST HAVE|KEY SKILLS)\s*(?:\n|:)',
                re.IGNORECASE
            )
            splits = sec_pattern.split(data.description)
            if len(splits) > 1:
                i = 1
                while i < len(splits):
                    header = splits[i].strip().upper()
                    content = splits[i+1].strip() if i+1 < len(splits) else ""
                    data.raw_sections[header] = content

                    if any(k in header for k in ["PREFERRED", "NICE TO HAVE", "DESIRED", "PLUS", "BONUS"]):
                        data.preferred_qualifications_text += ("\n" + content)
                        data.qualifications.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                    elif any(k in header for k in ["REQUIREMENT", "MINIMUM", "MUST", "QUALIFICATION"]):
                        data.basic_qualifications_text += ("\n" + content)
                        data.qualifications.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                    elif any(k in header for k in ["RESPONSIBIL", "WHAT YOU"]):
                        data.responsibilities.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                    i += 2

        # 5. Unavailable fields tracking
        for field_name, val in [("location", data.location), ("experience", data.experience),
                                ("employment_type", data.employment_type), ("responsibilities", data.responsibilities)]:
            if not val:
                data.unavailable_fields.append(field_name)

        if not data.title or not data.description or len(data.description) < 30:
            data.status = "error"
            data.error_message = (
                f"Could not extract sufficient job details from '{parsed.hostname}'. "
                "The page may require authentication, be protected by anti-bot verification, or contain no job posting."
            )
        elif not data.qualifications and not data.responsibilities:
            data.status = "partial"

        return data
