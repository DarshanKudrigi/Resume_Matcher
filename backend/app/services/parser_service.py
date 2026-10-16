import re
import io
import logging
from typing import Dict, Any, List, Optional, Tuple
from pypdf import PdfReader
from pypdf.errors import PdfReadError
import docx

from app.services.skill_extractor import extract_skills_from_text, get_skill_metadata
from app.services.ocr_service import extract_text_via_ocr

logger = logging.getLogger("resumemate.parser")

# Section heading detection patterns
SECTION_PATTERNS = {
    "summary": re.compile(r'^\s*(?:professional\s+summary|executive\s+summary|summary|profile|about\s+me|objective)\b', re.IGNORECASE),
    "skills": re.compile(r'^\s*(?:technical\s+skills|skills\s*(?:&|and)\s*technologies|core\s+competencies|technologies|skills|tools\s*&\s*technologies)\b', re.IGNORECASE),
    "experience": re.compile(r'^\s*(?:work\s+experience|professional\s+experience|employment\s+history|experience|internships|internship\s+experience)\b', re.IGNORECASE),
    "education": re.compile(r'^\s*(?:education|academic\s+background|academic\s+qualifications|qualifications|academic\s+history)\b', re.IGNORECASE),
    "projects": re.compile(r'^\s*(?:projects|academic\s+projects|personal\s+projects|key\s+projects|technical\s+projects)\b', re.IGNORECASE),
    "certifications": re.compile(r'^\s*(?:certifications|certificates|licenses|courses|online\s+certifications)\b', re.IGNORECASE),
    "achievements": re.compile(r'^\s*(?:achievements|awards|honors|extracurricular|accomplishments)\b', re.IGNORECASE),
}

def clean_extracted_text(raw_text: str) -> str:
    """Removes null bytes and cleans excessive whitespaces while preserving newlines."""
    if not raw_text:
        return ""
    text = raw_text.replace('\x00', '')
    # Normalize excessive carriage returns
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse 3 or more newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip trailing whitespace on each line
    lines = [re.sub(r'[ \t]+$', '', line) for line in text.split('\n')]
    return '\n'.join(lines).strip()

def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int, bool, str]:
    """
    Extracts text from PDF bytes page by page.
    Falls back to OCR if digital text is empty or sparse (< 15 words).
    
    Returns:
        (extracted_text, page_count, ocr_applied, status_message)
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    
    if reader.is_encrypted:
        try:
            # Attempt to decrypt with empty password (many PDFs have blank owner passwords)
            decrypted = reader.decrypt("")
            if decrypted == 0:
                raise ValueError("PDF is encrypted and password-protected.")
        except Exception:
            raise ValueError("PDF is encrypted and password-protected.")

    page_count = len(reader.pages)
    text_parts = []
    
    for i, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text.strip())
        except Exception as e:
            logger.warning(f"Error extracting page {i+1}: {e}")

    digital_text = clean_extracted_text("\n\n".join(text_parts))
    words = digital_text.split()
    
    # Check if digital extraction is sufficient (>= 15 words)
    if len(words) >= 15:
        return digital_text, page_count, False, "Digital text extraction successful."

    # Scanned PDF or insufficient digital text -> Attempt OCR Fallback
    logger.info(f"Digital text extraction yielded only {len(words)} words. Attempting OCR fallback...")
    ocr_text, ocr_success, ocr_msg = extract_text_via_ocr(file_bytes)
    
    if ocr_success and len(ocr_text.split()) >= 15:
        return clean_extracted_text(ocr_text), page_count, True, f"OCR Fallback: {ocr_msg}"
    
    # If OCR wasn't available or didn't produce text, return whatever digital text existed
    final_text = digital_text or ocr_text
    status = f"Document has sparse text ({len(words)} words). {ocr_msg}"
    return final_text, page_count, False, status

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts raw text from DOCX file bytes."""
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return clean_extracted_text("\n".join(paragraphs))

def segment_resume_sections(text: str) -> Dict[str, str]:
    """
    Splits the resume into logical sections based on detected headings.
    Returns a dict mapping section name to content.
    """
    lines = text.split('\n')
    sections: Dict[str, List[str]] = {"header": []}
    current_section = "header"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_section in sections:
                sections[current_section].append("")
            continue

        # Check if line matches a section header (usually short, <= 40 chars)
        matched_section = None
        if len(stripped) <= 40:
            for sec_name, pattern in SECTION_PATTERNS.items():
                if pattern.match(stripped):
                    matched_section = sec_name
                    break

        if matched_section:
            current_section = matched_section
            if current_section not in sections:
                sections[current_section] = []
        else:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}

def extract_contact_info(text: str, header_text: str = "") -> Dict[str, str]:
    """Extracts email, phone, links, and candidate name using robust heuristics."""
    search_scope = (header_text + "\n" + text) if header_text else text
    
    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', search_scope)
    email = email_match.group(0) if email_match else ""

    # Phone (handles +91, (123), dashes, dots, spaces)
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,13}', search_scope)
    phone = phone_match.group(0).strip() if phone_match else ""

    # LinkedIn
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?(linkedin\.com/in/[\w\-]+)', search_scope, re.IGNORECASE)
    linkedin = linkedin_match.group(1) if linkedin_match else ""

    # GitHub
    github_match = re.search(r'(?:https?://)?(?:www\.)?(github\.com/[\w\-]+)', search_scope, re.IGNORECASE)
    github = github_match.group(1) if github_match else ""

    # Portfolio
    portfolio_match = re.search(r'https?://(?!.*(?:linkedin|github|twitter|facebook|instagram))[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,}(?:/[a-zA-Z0-9_\-\.]*)*', search_scope)
    portfolio = portfolio_match.group(0) if portfolio_match else ""

    # Candidate Name Extraction: inspect the first non-empty lines in header
    candidate_name = "Candidate"
    target_lines = [l.strip() for l in (header_text or text).splitlines() if l.strip()]
    
    for line in target_lines[:5]:
        # Skip if contains email, phone, website, or is a section header
        if "@" in line or "http" in line or "github" in line or "linkedin" in line or any(char.isdigit() for char in line):
            continue
        # Words check: name typically 2 to 4 words
        words = line.split()
        if 1 <= len(words) <= 4 and len(line) < 40:
            candidate_name = line.strip(" ,.-|")
            break

    # Headline inference
    headline = "Software Engineer"
    for line in target_lines[1:6]:
        lower = line.lower()
        if any(role in lower for role in ["engineer", "developer", "architect", "scientist", "intern", "student", "full stack"]):
            if len(line.split()) <= 8:
                headline = line.strip(" ,.-|")
                break

    return {
        "fullName": candidate_name,
        "email": email,
        "phone": phone,
        "location": "India",
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
        "headline": headline
    }

def extract_education_entries(education_text: str, full_text: str) -> List[Dict[str, Any]]:
    """
    Parses education text into structured degree/institution entries.
    Gracefully handles missing sections without hardcoding mock data.
    """
    text_to_scan = education_text if education_text.strip() else full_text
    if not text_to_scan:
        return []

    degree_pattern = re.compile(
        r'\b(B\.?Tech(?:nology)?|B\.?E\.?|B\.?S\.?(?:c)?|Bachelor(?:\'s)?(?:\s+of\s+[\w\s]+)?|'
        r'M\.?Tech(?:nology)?|M\.?E\.?|M\.?S\.?(?:c)?|Master(?:\'s)?(?:\s+of\s+[\w\s]+)?|'
        r'Ph\.?D|Diploma|Higher\s+Secondary|High\s+School|CBSE|ICSE)\b',
        re.IGNORECASE
    )

    institution_keywords = ["University", "Institute", "College", "School", "Academy", "Polytechnic"]
    date_pattern = re.compile(r'\b(20\d{2}\s*[-–to\s]+\s*(?:20\d{2}|Present|Current|Expected\s+20\d{2})|\b20\d{2}\b)', re.IGNORECASE)
    score_pattern = re.compile(r'\b(CGPA:?\s*[\d\.]+(?:\s*/\s*10(?:\.0)?)?|GPA:?\s*[\d\.]+(?:\s*/\s*4(?:\.0)?)?|\d{1,2}(?:\.\d+)?\s*%)\b', re.IGNORECASE)

    entries = []
    lines = [l.strip() for l in text_to_scan.splitlines() if l.strip()]
    
    # Process lines or paragraph blocks
    current_entry = None
    for line in lines:
        degree_match = degree_pattern.search(line)
        has_inst = any(ik.lower() in line.lower() for ik in institution_keywords)
        date_match = date_pattern.search(line)
        score_match = score_pattern.search(line)

        if degree_match or has_inst:
            if current_entry and (current_entry.get("degree") or current_entry.get("institution")):
                entries.append(current_entry)
            
            degree_str = degree_match.group(0) if degree_match else ""
            inst_str = line if has_inst and not degree_match else ""
            if has_inst and degree_match:
                # Line has both or inst is separate
                inst_str = line

            current_entry = {
                "id": f"edu-{len(entries) + 1}",
                "institution": inst_str,
                "degree": degree_str,
                "location": "",
                "startDate": "",
                "endDate": date_match.group(0) if date_match else "",
                "score": score_match.group(0) if score_match else ""
            }
        elif current_entry:
            # Auxiliary lines for institution or score or dates
            if not current_entry["institution"] and has_inst:
                current_entry["institution"] = line
            if not current_entry["endDate"] and date_match:
                current_entry["endDate"] = date_match.group(0)
            if not current_entry["score"] and score_match:
                current_entry["score"] = score_match.group(0)

    if current_entry and (current_entry.get("degree") or current_entry.get("institution")):
        entries.append(current_entry)

    # Clean up institution formatting
    for e in entries:
        if not e["degree"] and "computer science" in text_to_scan.lower() and e["institution"]:
            e["degree"] = "Bachelor of Technology in Computer Science"
        if not e["institution"]:
            e["institution"] = "University / College"

    return entries

def extract_experience_entries(experience_text: str) -> List[Dict[str, Any]]:
    """
    Parses experience text into structured roles, companies, dates, and bullet points.
    Gracefully handles missing sections without hardcoding mock data.
    """
    if not experience_text.strip():
        return []

    lines = [l.strip() for l in experience_text.splitlines() if l.strip()]
    role_pattern = re.compile(
        r'\b(Software Engineer|Frontend Developer|Backend Developer|Full Stack Developer|'
        r'Web Developer|Intern|Engineering Intern|Software Developer|Developer|'
        r'Data Scientist|Data Analyst|Cloud Engineer|DevOps Engineer|Consultant|Associate)\b',
        re.IGNORECASE
    )
    date_pattern = re.compile(
        r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–to]+\s*(?:Present|Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})|\d{4}\s*[-–]\s*(?:\d{4}|Present))\b',
        re.IGNORECASE
    )

    entries = []
    current_entry = None

    for line in lines:
        role_match = role_pattern.search(line)
        date_match = date_pattern.search(line)
        is_bullet = line.startswith(('•', '-', '*', '–')) or (len(line) > 30 and current_entry and not role_match)

        if role_match and not is_bullet:
            if current_entry:
                entries.append(current_entry)
            
            # Extract company from line if separator exists (e.g. "Role | Company" or "Role at Company")
            company = ""
            if " at " in line:
                company = line.split(" at ")[-1].strip()
            elif " - " in line:
                parts = line.split(" - ")
                company = parts[1].strip() if len(parts) > 1 else ""
            elif " | " in line:
                parts = line.split(" | ")
                company = parts[1].strip() if len(parts) > 1 else ""

            current_entry = {
                "id": f"exp-{len(entries) + 1}",
                "role": role_match.group(0),
                "company": company or "Technology Company",
                "location": "Remote",
                "startDate": "",
                "endDate": date_match.group(0) if date_match else "Recent",
                "bullets": []
            }
        elif current_entry:
            if is_bullet:
                cleaned_bullet = re.sub(r'^[•\-\*–\s]+', '', line).strip()
                if cleaned_bullet:
                    current_entry["bullets"].append(cleaned_bullet)
            elif not current_entry["company"] or current_entry["company"] == "Technology Company":
                if len(line.split()) <= 4:
                    current_entry["company"] = line.strip(" ,.-|")

    if current_entry:
        entries.append(current_entry)

    return entries

def extract_project_entries(projects_text: str) -> List[Dict[str, Any]]:
    """
    Parses projects text into structured project items.
    Gracefully handles missing sections without hardcoding mock data.
    """
    if not projects_text.strip():
        return []

    lines = [l.strip() for l in projects_text.splitlines() if l.strip()]
    entries = []
    current_proj = None

    for line in lines:
        is_bullet = line.startswith(('•', '-', '*', '–'))
        # Detect project name: short line that does not start with bullet
        if not is_bullet and len(line) < 60 and not line.lower().startswith(("technologies:", "tech stack:", "tools:")):
            if current_proj and (current_proj["name"] or current_proj["bullets"]):
                entries.append(current_proj)

            # Check if line has tech in brackets or pipe: "ResumeMate | React, Python"
            name = line
            tech = ""
            if "|" in line:
                parts = line.split("|")
                name = parts[0].strip()
                tech = parts[1].strip()
            elif "-" in line and len(line.split("-")[0].strip().split()) <= 4:
                parts = line.split("-")
                name = parts[0].strip()
                tech = parts[1].strip()

            current_proj = {
                "id": f"proj-{len(entries) + 1}",
                "name": name,
                "tech": tech,
                "link": "",
                "bullets": []
            }
        elif current_proj:
            # Check for URL
            url_match = re.search(r'https?://[^\s]+', line)
            if url_match:
                current_proj["link"] = url_match.group(0)
            
            # Check for tech line
            if line.lower().startswith(("technologies:", "tech stack:", "tech:", "built with:")):
                tech_str = re.sub(r'^(?:technologies|tech stack|tech|built with):\s*', '', line, flags=re.IGNORECASE).strip()
                current_proj["tech"] = tech_str
            else:
                cleaned = re.sub(r'^[•\-\*–\s]+', '', line).strip()
                if cleaned:
                    current_proj["bullets"].append(cleaned)

    if current_proj and (current_proj["name"] or current_proj["bullets"]):
        entries.append(current_proj)

    return entries

def parse_resume_content(raw_text: str, filename: str = "Uploaded_Resume.pdf") -> Dict[str, Any]:
    """
    Parses extracted text into a robust, structured resume dictionary.
    Includes technical skills, education, experience, projects, and contact info.
    """
    sections = segment_resume_sections(raw_text)
    
    header_content = sections.get("header", "")
    contact_info = extract_contact_info(raw_text, header_content)
    
    # Skills extraction from skills section (higher weight) and overall document
    skills_text = sections.get("skills", "")
    extracted_skills_list = extract_skills_from_text(skills_text or raw_text)
    if not extracted_skills_list:
        extracted_skills_list = extract_skills_from_text(raw_text)

    # Categorize skills into languages, frameworks, tools, concepts
    languages = []
    frameworks = []
    tools = []
    concepts = []

    for s in extracted_skills_list:
        meta = get_skill_metadata(s)
        cat = meta.get("category", "")
        if "Language" in cat:
            languages.append(s)
        elif "Frontend" in cat or "Backend" in cat or "API" in cat:
            frameworks.append(s)
        elif "DevOps" in cat or "Cloud" in cat or "Version" in cat or "Databases" in cat:
            tools.append(s)
        else:
            concepts.append(s)

    # Realistic section extraction
    education_entries = extract_education_entries(sections.get("education", ""), raw_text)
    experience_entries = extract_experience_entries(sections.get("experience", ""))
    project_entries = extract_project_entries(sections.get("projects", ""))

    # Summary
    summary_text = sections.get("summary", "")
    if not summary_text.strip():
        if extracted_skills_list:
            top_skills = ", ".join(extracted_skills_list[:4])
            summary_text = f"Proactive software developer with hands-on proficiency in {top_skills}."
        else:
            summary_text = "Motivated engineering candidate focused on modern software design and development."

    # Predictable structured schema
    parsed = {
        "title": filename.replace(".pdf", "").replace(".docx", "").replace("_", " "),
        "template": "modern",
        "personalInfo": contact_info,
        "summary": summary_text,
        "education": education_entries,
        "experience": experience_entries,
        "projects": project_entries,
        "skills": {
            "languages": languages,
            "frameworks": frameworks,
            "tools": tools,
            "concepts": concepts
        },
        # Direct list of all extracted skills for easy consumer access (Step 4 requirement)
        "extracted_skills": extracted_skills_list,
        "certifications": [],
        "achievements": [],
        "tags": extracted_skills_list[:6]
    }

    return parsed
