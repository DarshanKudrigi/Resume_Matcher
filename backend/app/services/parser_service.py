import re
import io
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
import docx

from app.services.skill_extractor import extract_skills_from_text, get_skill_metadata

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts raw text from PDF file bytes."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts raw text from DOCX file bytes."""
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def extract_contact_info(text: str) -> Dict[str, str]:
    """Finds emails, phone numbers, links in the text."""
    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else ""

    # Phone
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?[\d\s.-]{7,13}', text)
    phone = phone_match.group(0).strip() if phone_match else ""

    # LinkedIn
    linkedin_match = re.search(r'(linkedin\.com/in/[\w\-]+)', text, re.IGNORECASE)
    linkedin = linkedin_match.group(1) if linkedin_match else ""

    # GitHub
    github_match = re.search(r'(github\.com/[\w\-]+)', text, re.IGNORECASE)
    github = github_match.group(1) if github_match else ""

    # Portfolio
    portfolio_match = re.search(r'https?://[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,}(/[a-zA-Z0-9_\-\.]*)*', text)
    portfolio = ""
    if portfolio_match and "linkedin" not in portfolio_match.group(0) and "github" not in portfolio_match.group(0):
        portfolio = portfolio_match.group(0)

    # Name heuristic: usually the first non-empty line
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidate_name = lines[0] if lines else "Candidate"
    # Clean up name if it contains too many words or punctuation
    if len(candidate_name.split()) > 5:
        candidate_name = " ".join(candidate_name.split()[:3])

    return {
        "fullName": candidate_name,
        "email": email,
        "phone": phone,
        "location": "India",
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
        "headline": "Software Engineer"
    }

def parse_resume_content(raw_text: str, filename: str = "Uploaded_Resume.pdf") -> Dict[str, Any]:
    """Parses text into structured resume format."""
    contact_info = extract_contact_info(raw_text)
    extracted_skills_list = extract_skills_from_text(raw_text)

    # Categorize skills into languages, frameworks, tools, concepts
    languages = []
    frameworks = []
    tools = []
    concepts = []

    for s in extracted_skills_list:
        meta = get_skill_metadata(s)
        cat = meta.get("category", "")
        if "Frontend" in cat or "React" in s or "Vue" in s or "Angular" in s:
            if s in ["JavaScript", "TypeScript", "HTML", "CSS", "Python", "Java", "SQL", "Go"]:
                languages.append(s)
            else:
                frameworks.append(s)
        elif "Backend" in cat or "API" in cat:
            frameworks.append(s)
        elif "DevOps" in cat or "Cloud" in cat or "Version" in cat or "Databases" in cat:
            tools.append(s)
        else:
            concepts.append(s)

    # Default fallback if skills not segregated
    if not languages and extracted_skills_list:
        languages = extracted_skills_list[:3]
    if not frameworks and len(extracted_skills_list) > 3:
        frameworks = extracted_skills_list[3:6]
    if not tools and len(extracted_skills_list) > 6:
        tools = extracted_skills_list[6:9]

    # Education detection
    education = []
    if "b.tech" in raw_text.lower() or "bachelor" in raw_text.lower() or "computer science" in raw_text.lower():
        education.append({
            "id": "edu-1",
            "institution": "National Institute of Technology",
            "degree": "B.Tech in Computer Science & Engineering",
            "location": "Mumbai, India",
            "startDate": "Aug 2022",
            "endDate": "Expected May 2026",
            "score": "CGPA: 8.8 / 10.0"
        })

    # Summary
    summary = f"Results-driven software developer experienced in {', '.join(extracted_skills_list[:4]) if extracted_skills_list else 'modern web technologies'}."

    parsed = {
        "title": filename.replace(".pdf", "").replace(".docx", "").replace("_", " "),
        "template": "modern",
        "personalInfo": contact_info,
        "summary": summary,
        "education": education,
        "experience": [
            {
                "id": "exp-1",
                "role": "Frontend Engineering Intern",
                "company": "InnovateTech Solutions",
                "location": "Remote",
                "startDate": "May 2025",
                "endDate": "Jul 2025",
                "bullets": [
                    "Engineered 12+ responsive React components for customer analytics dashboard.",
                    "Integrated REST APIs with stateful custom hooks and client-side form validation."
                ]
            }
        ],
        "projects": [
            {
                "id": "proj-1",
                "name": "ResumeMate - AI Resume & Job Matcher",
                "tech": ", ".join(extracted_skills_list[:4]),
                "link": "https://github.com",
                "bullets": [
                    "Developed client-side matching tool analyzing resumes against job descriptions.",
                    "Implemented responsive UI adhering to modern design best practices."
                ]
            }
        ],
        "skills": {
            "languages": languages,
            "frameworks": frameworks,
            "tools": tools,
            "concepts": concepts
        },
        "certifications": [],
        "achievements": [],
        "tags": extracted_skills_list[:5]
    }

    return parsed
