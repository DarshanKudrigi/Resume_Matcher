import re
import urllib.parse
from typing import List
from .base_strategy import BaseJobStrategy, RawJobData

class LeverStrategy(BaseJobStrategy):
    name: str = "Lever"

    def can_handle(self, parsed_url: urllib.parse.ParseResult) -> bool:
        host = (parsed_url.hostname or "").lower()
        return host == "jobs.lever.co" or host.endswith(".lever.co")

    def extract(self, page, url: str) -> RawJobData:
        data = RawJobData(url=url, source="Lever")
        parsed = urllib.parse.urlparse(url)
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]

        # In Lever, URL is typically /<company_slug>/<job_id>
        if len(path_parts) >= 1:
            data.company = path_parts[0].replace("-", " ").title()
        if len(path_parts) >= 2:
            data.job_id = path_parts[1]

        try:
            page.wait_for_selector(".posting-headline, .section.page-centered, h2", timeout=12000)
        except Exception:
            pass

        # 1. Company Logo / Name override
        logo_el = page.query_selector(".main-header-logo img")
        if logo_el:
            alt = logo_el.get_attribute("alt") or ""
            if alt:
                # "Drivetrain logo" -> "Drivetrain"
                data.company = re.sub(r'\s*logo\s*', '', alt, flags=re.IGNORECASE).strip()

        # 2. Job Title
        title_el = page.query_selector(".posting-headline h2, h2.posting-title, h2")
        if title_el:
            data.title = title_el.inner_text().strip()
        if not data.title:
            page_title = page.title() or ""
            data.title = re.sub(r'\s*-\s*Lever.*', '', page_title, flags=re.IGNORECASE).strip()

        # Clean title of auxiliary categories if captured
        if data.title:
            data.title = data.title.split('\n')[0].strip()

        # 3. Location, Commitment (Employment Type), Department
        cat_el = page.query_selector(".posting-categories")
        if cat_el:
            loc_el = cat_el.query_selector(".location")
            if loc_el:
                data.location = loc_el.inner_text().strip()

            commit_el = cat_el.query_selector(".commitment")
            if commit_el:
                data.employment_type = commit_el.inner_text().strip()

            dept_el = cat_el.query_selector(".department")
            if dept_el:
                data.raw_sections["department"] = dept_el.inner_text().strip()

            workplace_el = cat_el.query_selector(".workplaceTypes")
            if workplace_el:
                wpt = workplace_el.inner_text().strip()
                if data.location:
                    data.location += f" ({wpt})"
                else:
                    data.location = wpt

        # 4. Description and Sections (.section.page-centered)
        sections = page.query_selector_all(".section.page-centered, [data-qa='job-description']")
        all_text_parts: List[str] = []
        resp_list: List[str] = []
        quals_list: List[str] = []

        if sections:
            for sec in sections:
                heading_el = sec.query_selector("h3, h4, h5, .section-header")
                heading_text = heading_el.inner_text().strip().upper() if heading_el else ""
                
                # Get bullet points or paragraph text
                content_text = sec.inner_text().strip()
                all_text_parts.append(content_text)

                bullets = [li.inner_text().strip() for li in sec.query_selector_all("li") if li.inner_text().strip()]

                if heading_text:
                    data.raw_sections[heading_text] = content_text

                    if any(k in heading_text for k in ["RESPONSIBIL", "WHAT YOU'LL DO", "ROLE", "DUTIES"]):
                        resp_list.extend(bullets if bullets else [content_text])
                    elif any(k in heading_text for k in ["NICE TO HAVE", "PREFERRED", "BONUS", "DESIRED", "PLUS"]):
                        data.preferred_qualifications_text += ("\n" + content_text)
                        quals_list.extend(bullets if bullets else [content_text])
                    elif any(k in heading_text for k in ["QUALIFICATION", "REQUIREMENT", "YOU ARE", "YOU HAVE", "WHAT WE'RE LOOKING FOR", "MUST"]):
                        data.basic_qualifications_text += ("\n" + content_text)
                        quals_list.extend(bullets if bullets else [content_text])
        else:
            # Fallback to main body text
            body_el = page.query_selector(".content, main, body")
            if body_el:
                all_text_parts.append(body_el.inner_text().strip())

        data.description = "\n\n".join(all_text_parts).strip()
        data.responsibilities = resp_list
        data.qualifications = quals_list

        # If basic qualifications text wasn't extracted by heading, use regex on full description
        if not data.basic_qualifications_text and data.description:
            sec_pattern = re.compile(
                r'(?:^|\n)\s*(RESPONSIBILITIES|REQUIREMENTS|QUALIFICATIONS|NICE TO HAVE|BONUS POINTS|WHAT YOU BRING)\s*(?:\n|:)',
                re.IGNORECASE
            )
            splits = sec_pattern.split(data.description)
            if len(splits) > 1:
                i = 1
                while i < len(splits):
                    header = splits[i].strip().upper()
                    content = splits[i+1].strip() if i+1 < len(splits) else ""
                    if any(k in header for k in ["REQUIREMENT", "QUALIFICATION", "WHAT YOU BRING"]):
                        data.basic_qualifications_text += ("\n" + content)
                    elif any(k in header for k in ["NICE", "BONUS", "PREFERRED"]):
                        data.preferred_qualifications_text += ("\n" + content)
                    elif "RESPONSIBIL" in header and not data.responsibilities:
                        data.responsibilities.extend([b.strip("- •*\t") for b in content.splitlines() if b.strip("- •*\t")])
                    i += 2

        # Unavailable fields detection
        for field_name, val in [("location", data.location), ("experience", data.experience),
                                ("employment_type", data.employment_type), ("responsibilities", data.responsibilities)]:
            if not val:
                data.unavailable_fields.append(field_name)

        if not data.title or not data.description:
            data.status = "error"
            data.error_message = "Failed to extract required job title and description from Lever posting."
        elif not data.responsibilities and not data.qualifications:
            data.status = "partial"

        return data
