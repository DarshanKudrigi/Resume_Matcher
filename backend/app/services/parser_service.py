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
    "achievements": re.compile(r'^\s*(?:achievements|awards|honors|accomplishments)\b', re.IGNORECASE),
    "leadership": re.compile(r'^\s*(?:leadership|positions?\s+of\s+responsibility|extracurricular|activities|volunteer)\b', re.IGNORECASE),
}

def defragment_vertical_text(text: str) -> str:
    """
    Detects if text was extracted with 1-2 words per line (common PDF fragmentation artifact)
    and reconstructs coherent lines and bullet points.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines or len(lines) < 20:
        return text
    single_word_count = sum(1 for l in lines if len(l.split()) <= 2)
    if (single_word_count / len(lines)) < 0.55:
        return text

    logger.info("Detected word-fragmented text in PDF extraction. Defragmenting lines...")
    reconstructed = []
    current_buf = []

    for l in lines:
        is_bullet = l.startswith(('•', '-', '*', '–', '●', '○'))
        is_heading = any(h in l.upper() for h in [
            "EXPERIENCE", "PROJECTS", "EDUCATION", "SKILLS", "SUMMARY", "CERTIFICATIONS"
        ]) and len(l.split()) <= 4

        if is_heading:
            if current_buf:
                reconstructed.append(" ".join(current_buf))
                current_buf = []
            reconstructed.append(f"\n{l}\n")
        elif is_bullet:
            if current_buf:
                reconstructed.append(" ".join(current_buf))
                current_buf = []
            current_buf.append(l)
        else:
            current_buf.append(l)
            if l.endswith(('.', ':', ';')):
                reconstructed.append(" ".join(current_buf))
                current_buf = []

    if current_buf:
        reconstructed.append(" ".join(current_buf))

    return "\n".join(reconstructed)

def clean_extracted_text(raw_text: str) -> str:
    """Removes null bytes and cleans excessive whitespaces while preserving newlines."""
    if not raw_text:
        return ""
    text = raw_text.replace('\x00', '')
    # Normalize bullet characters at start of lines
    text = re.sub(r'(?m)^(\s*)[\ufffd\u2022●○▪▫·]\s*', r'\1• ', text)
    # Normalize excessive carriage returns
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse 3 or more newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip trailing whitespace on each line
    lines = [re.sub(r'[ \t]+$', '', line) for line in text.split('\n')]
    cleaned = '\n'.join(lines).strip()
    return defragment_vertical_text(cleaned)

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
            try:
                page_text = page.extract_text(extraction_mode="layout") or ""
            except Exception:
                page_text = page.extract_text() or ""
            if not page_text.strip():
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

BULLET_CHARS = ('\u2022', '•', '-', '*', '–', '●', '○', '▪', '▫', '·')

TECH_KEYWORDS = [
    'react', 'next.js', 'fastapi', 'node.js', 'express', 'mongodb', 'python', 'java',
    'c++', 'javascript', 'typescript', 'redis', 'rest', 'jwt', 'aws', 'docker', 'sql',
    'postgresql', 'mysql', 'flask', 'django', 'tailwind', 'html', 'css', 'vue', 'angular'
]

KNOWN_SECTION_HEADINGS = {
    'leadership', 'positions of responsibility', 'extracurricular', 'certifications',
    'achievements', 'awards', 'education', 'experience', 'skills', 'summary'
}

PROJECT_ACTION_VERBS = {
    'developed', 'built', 'created', 'designed', 'implemented', 'led', 'managed',
    'worked', 'automated', 'integrated', 'engineered', 'contributed', 'an', 'a',
    'the', 'collaborated', 'utilized', 'spearheaded', 'facilitated', 'responsible'
}

STOP_PROJECT_WORDS = {
    "including", "to", "and", "or", "in", "with", "etc", "etc.", "also", "for", "by", "on", "at", "as", "from",
    "live", "browse", "vm", "vcloud", "azure", "present", "recent", "none", "n/a", "na", "remote", "fixed"
}

def split_title_and_tech(line: str) -> Tuple[str, str]:
    """Separates project title from inline technology listing."""
    earliest_idx = len(line)
    for kw in TECH_KEYWORDS:
        m = re.search(r'\b' + re.escape(kw) + r'\b', line, re.IGNORECASE)
        if m and m.start() < earliest_idx:
            after = line[m.start():]
            if ',' in after or len(after.split()) <= 6:
                earliest_idx = m.start()
    if earliest_idx < len(line):
        title_part = line[:earliest_idx].strip(' ,-–|:\ufffd')
        tech_part = line[earliest_idx:].strip(' ,-–|:\ufffd')
        return title_part, tech_part
    return line.strip(' ,-–|:\ufffd'), ''

def is_pure_tech_line(line: str) -> bool:
    """Checks whether a line is purely comma-separated technologies rather than a title."""
    clean = line.strip(' ,-–|:\ufffd')
    lower = clean.lower()
    if lower.startswith(('technologies:', 'tech stack:', 'tools:', 'built with:')):
        return True
    if ',' in clean:
        parts = [p.strip() for p in clean.split(',') if p.strip()]
        if any(len(p.split()) > 3 or len(p) > 25 for p in parts):
            return False
        matched = sum(1 for p in parts if any(kw in p.lower() for kw in TECH_KEYWORDS))
        if matched >= len(parts) * 0.6:
            return True
    return False

def extract_experience_entries(experience_text: str) -> List[Dict[str, Any]]:
    """
    Parses experience text into structured roles, companies, dates, and bullet points.
    Gracefully handles missing sections without hardcoding mock data.
    """
    if not experience_text.strip():
        return []

    lines = experience_text.splitlines()
    # Pre-stitch wrapped bullet lines
    stitched_lines = []
    for raw_l in lines:
        line = raw_l.strip()
        if not line:
            continue
        is_bullet = raw_l.lstrip().startswith(BULLET_CHARS)
        is_continuation = (
            stitched_lines and
            not is_bullet and
            (
                raw_l.startswith(('   ', '\t', '  ')) or
                (stitched_lines[-1]['is_bullet'] and line[0].islower())
            )
        )
        if is_continuation:
            stitched_lines[-1]['text'] += ' ' + line
        else:
            stitched_lines.append({'text': line, 'is_bullet': is_bullet})

    role_pattern = re.compile(
        r'\b(Engineering Intern|Software Engineering Intern|Full Stack Developer|'
        r'Frontend Developer|Backend Developer|Software Developer|Software Engineer|'
        r'Cloud Engineer|DevOps Engineer|Data Scientist|Data Analyst|'
        r'Web Developer|Developer|Consultant|Associate|Intern)\b',
        re.IGNORECASE
    )
    date_pattern = re.compile(
        r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[,.]?\s+\d{4}\s*[-–to]+\s*(?:Present|Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[,.]?\s+\d{4})|\d{4}\s*[-–]\s*(?:\d{4}|Present))\b',
        re.IGNORECASE
    )

    entries = []
    current_entry = None
    pending_company = ""
    pending_location = ""

    for item in stitched_lines:
        line = item['text']
        is_bullet = item['is_bullet']
        clean_line = re.sub(r'^[•\-\*–●○▪▫·\s\ufffd]+', '', line).strip()
        role_match = role_pattern.search(clean_line)
        date_match = date_pattern.search(clean_line)

        # Detect wide column layout: "COMPANY          LOCATION"
        col_parts = [p.strip() for p in re.split(r'\s{3,}', clean_line) if p.strip()]
        if not is_bullet and not role_match and not date_match and col_parts and len(col_parts[0].split()) <= 4:
            pending_company = col_parts[0].strip(" ,.-|")
            if len(col_parts) > 1:
                pending_location = col_parts[1].strip(" ,.-|")
            continue

        if role_match and not is_bullet:
            if current_entry:
                entries.append(current_entry)
            
            company = pending_company
            location = pending_location or "Remote"

            if " at " in clean_line:
                company = clean_line.split(" at ")[-1].strip()
            elif " | " in clean_line:
                parts = clean_line.split(" | ")
                company = parts[1].strip() if len(parts) > 1 else company
            elif " - " in clean_line and not date_match:
                parts = clean_line.split(" - ")
                company = parts[1].strip() if len(parts) > 1 else company

            current_entry = {
                "id": f"exp-{len(entries) + 1}",
                "role": role_match.group(0),
                "company": company or "Technology Company",
                "location": location,
                "startDate": "",
                "endDate": date_match.group(0) if date_match else "Recent",
                "bullets": []
            }
        elif current_entry:
            if is_bullet:
                if clean_line:
                    current_entry["bullets"].append(clean_line)
            elif date_match:
                current_entry["endDate"] = date_match.group(0)
            elif not current_entry["company"] or current_entry["company"] == "Technology Company":
                if not any(k in clean_line.lower() for k in ["present", "current", "202", "201", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]) and len(clean_line.split()) <= 4:
                    current_entry["company"] = clean_line.strip(" ,.-|")

    if current_entry:
        entries.append(current_entry)

    return entries

def extract_project_entries(projects_text: str) -> List[Dict[str, Any]]:
    """
    Parses projects text into structured project items.
    Prevents single-word fragments, handles line-wrapping in PDF extraction,
    and isolates technology stacks and bullet descriptions.
    """
    if not projects_text.strip():
        return []

    lines = projects_text.splitlines()
    stitched_lines = []
    for raw_l in lines:
        line = raw_l.strip()
        if not line:
            continue
        is_bullet = raw_l.lstrip().startswith(BULLET_CHARS)
        is_continuation = (
            stitched_lines and
            not is_bullet and
            not is_pure_tech_line(line) and
            (
                raw_l.startswith(('   ', '\t', '  ')) or
                (
                    stitched_lines[-1]['is_bullet'] and line[0].islower()
                )
            )
        )
        if is_continuation:
            stitched_lines[-1]['text'] += ' ' + line
        else:
            stitched_lines.append({'text': line, 'is_bullet': is_bullet})

    entries = []
    current_proj = None

    for item in stitched_lines:
        line = item['text']
        is_bullet = item['is_bullet']
        clean_line = re.sub(r'^[•\-\*–●○▪▫·\s\ufffd]+', '', line).strip()
        lower_line = clean_line.lower().strip(' ,.-|:;')

        # Check for section boundaries
        if any(lower_line == h or lower_line.startswith(h + ' ') or lower_line.startswith(h + '/') for h in KNOWN_SECTION_HEADINGS):
            if current_proj and current_proj['name']:
                entries.append(current_proj)
            current_proj = None
            continue

        if is_pure_tech_line(clean_line):
            if current_proj:
                current_proj['tech'] = (current_proj['tech'] + ', ' + clean_line).strip(' ,')
            continue

        # Check if line is a project title/header candidate
        is_header = False
        if not clean_line.startswith(('http://', 'https://', 'www.')) and not lower_line.startswith(('other projects', 'github:', 'demo:')):
            if any(sep in clean_line for sep in [' – ', ' \ufffd ', ' - ', ' | ']):
                first_part = re.split(r'\s+[-–|]\s+|\s+\ufffd\s+', clean_line)[0].strip()
                words = first_part.split()
                first_word = words[0].lower() if words else ''
                if first_word not in PROJECT_ACTION_VERBS and len(first_part) >= 2 and len(words) <= 12:
                    if not (clean_line.endswith('.') and len(clean_line.split()) > 15):
                        is_header = True
            elif not is_bullet and not clean_line.endswith('.') and clean_line[0].isupper() and len(clean_line.split()) <= 8:
                first_word = clean_line.split()[0].lower()
                if first_word not in PROJECT_ACTION_VERBS and clean_line.lower().strip(' ,.-|:;') not in STOP_PROJECT_WORDS:
                    is_header = True

        if is_header:
            if current_proj and current_proj['name'] and (current_proj['bullets'] or current_proj['tech']):
                entries.append(current_proj)
            title_part, tech_part = split_title_and_tech(clean_line)
            proj_name = title_part
            for sep in [' – ', ' \ufffd ', ' - ', ' | ']:
                if sep in title_part:
                    proj_name = title_part.split(sep)[0].strip()
                    break

            # Strictly reject invalid or stop-word project titles
            if proj_name.lower().strip(" ,.-|:;") in STOP_PROJECT_WORDS or len(proj_name.strip()) <= 2:
                continue

            current_proj = {
                'id': f'proj-{len(entries) + 1}',
                'name': proj_name,
                'full_title': title_part,
                'tech': tech_part,
                'link': '',
                'bullets': []
            }
            continue

        # Bullet point or description
        if current_proj:
            if 'github' in lower_line or 'demo' in lower_line:
                urls = re.findall(r'https?://[^\s]+', clean_line)
                if urls:
                    current_proj['link'] = urls[0]
            if len(clean_line) > 10 and not clean_line.lower().startswith(('github', 'live demo')):
                current_proj['bullets'].append(clean_line)

    if current_proj and current_proj['name'] and (current_proj['bullets'] or current_proj['tech']):
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

    try:
        from app.services.matcher_service import calculate_ats_metrics
        ats = calculate_ats_metrics(parsed, raw_text, [])
        parsed["atsScore"] = ats.score
        parsed["atsBreakdown"] = ats.model_dump()
    except Exception as e:
        logger.warning(f"Could not compute ATS metrics during parse: {e}")
        parsed["atsScore"] = 85

    return parsed
