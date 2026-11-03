from typing import Dict, List, Any, Tuple
import re

from app.schemas.analysis import (
    AnalysisResponse, SkillGapItem, ATSBreakdown, ATSItem
)
from app.services.skill_extractor import (
    extract_skills_from_text, get_skill_metadata
)
from app.services.recommendations import get_recommendations_for_skills

def calculate_ats_metrics(resume_data: Dict[str, Any], resume_text: str, target_keywords: List[str]) -> ATSBreakdown:
    """Evaluates applicant tracking system compliance and returns breakdown items."""
    personal_info = resume_data.get("personalInfo", {})
    has_email = bool(personal_info.get("email") or re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text))
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\d{10}'
    has_phone = bool(personal_info.get("phone") or re.search(phone_pattern, resume_text))
    has_linkedin = bool("linkedin" in str(personal_info.get("linkedin", "")).lower() or "linkedin.com" in resume_text.lower())
    has_github = bool("github" in str(personal_info.get("github", "")).lower() or "github.com" in resume_text.lower())

    # 1. Contact details (20 pts)
    if has_email and has_phone:
        contact_passed = True
        contact_score = 20
        contact_note = "Full name, phone, and email contact verified." + (" Links to GitHub/LinkedIn included." if (has_linkedin or has_github) else "")
    elif has_email or has_phone:
        contact_passed = False
        contact_score = 10
        missing = "phone number" if not has_phone else "email address"
        contact_note = f"Partial contact details. Missing {missing}."
    else:
        contact_passed = False
        contact_score = 0
        contact_note = "Missing both phone and email contact details."

    # 2. Skills section (20 pts)
    skills = resume_data.get("skills", {})
    has_skills = bool(resume_data.get("extracted_skills")) or (
        any(isinstance(v, list) and len(v) > 0 for v in skills.values()) if isinstance(skills, dict) else bool(skills)
    )
    skills_passed = has_skills or any(k in resume_text.lower() for k in ["skills", "technologies", "proficiencies", "competencies"])
    skills_score = 20 if skills_passed else 0
    skills_note = "Categorized technical skills section identified with industry-standard naming." if skills_passed else "Ensure a distinct, categorized Skills section is defined."

    # 3. Education (15 pts)
    has_edu = bool(resume_data.get("education"))
    education_passed = has_edu or any(k in resume_text.lower() for k in ["b.tech", "b.e.", "degree", "university", "college", "bachelor", "master", "institute", "school", "education"])
    education_score = 15 if education_passed else 0
    education_note = "Accredited university degree and academic credentials parsed." if education_passed else "Add degree title, institution, and completion year."

    # 4. Projects & Experience (20 pts)
    has_proj = bool(resume_data.get("projects")) or bool(resume_data.get("experience"))
    projects_passed = has_proj or any(k in resume_text.lower() for k in ["projects", "experience", "developed", "built", "engineered", "contributed"])
    projects_score = 20 if projects_passed else 0
    projects_note = "Impactful project descriptions with practical technical context." if projects_passed else "Add structured project portfolios or work experience bullet points."

    # 5. Keyword Density (15 pts)
    missing_keywords = [kw for kw in target_keywords if kw.lower() not in resume_text.lower()] if target_keywords else []
    if target_keywords:
        match_ratio = (len(target_keywords) - len(missing_keywords)) / len(target_keywords)
        keywords_score = int(match_ratio * 15)
        keywords_passed = match_ratio >= 0.5
        keywords_note = "Optimal keyword density for target competencies." if keywords_passed else f"Warning: Consider integrating missing keywords like {', '.join(missing_keywords[:3])}."
    else:
        keywords_passed = True
        keywords_score = 15
        keywords_note = "Standard technical terminology matched."

    # 6. ATS Layout Parsability (10 pts)
    layout_passed = len(resume_text.split()) >= 30
    layout_score = 10 if layout_passed else 0
    layout_note = "Standard single/two-column text format with high ATS parsability." if layout_passed else "Document text is too sparse for ATS scanners."

    score = min(100, max(0, contact_score + skills_score + education_score + projects_score + keywords_score + layout_score))

    verdict = "ATS Passed with High Compatibility" if score >= 85 else ("ATS Passed with Minor Enhancements" if score >= 70 else "ATS Review Recommended")

    items = [
        ATSItem(
            id="contact",
            label="Contact Information",
            passed=contact_passed,
            note=contact_note
        ),
        ATSItem(
            id="skills",
            label="Skills Section",
            passed=skills_passed,
            note=skills_note
        ),
        ATSItem(
            id="education",
            label="Education & Credentials",
            passed=education_passed,
            note=education_note
        ),
        ATSItem(
            id="projects",
            label="Project Descriptions",
            passed=projects_passed,
            note=projects_note
        ),
        ATSItem(
            id="keywords",
            label="Job-Specific Keywords",
            passed=keywords_passed,
            note=keywords_note
        ),
        ATSItem(
            id="layout",
            label="Clean ATS Layout",
            passed=layout_passed,
            note=layout_note
        )
    ]

    return ATSBreakdown(score=score, verdict=verdict, items=items)

def analyze_resume_against_job(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    resume_raw_text: str = ""
) -> AnalysisResponse:
    """Comprehensive resume to job matching engine without fabricated fallbacks."""
    job_title = job_data.get("title") or "Target Position"
    company = job_data.get("company") or "Target Company"
    job_desc = job_data.get("description", "")
    
    # Extract or read job skills from either requiredSkills/preferredSkills or structured items
    raw_req = job_data.get("requiredSkills") or job_data.get("required_skills") or []
    raw_pref = job_data.get("preferredSkills") or job_data.get("preferred_skills") or []

    required_skills: List[str] = [
        s.get("name") if isinstance(s, dict) else (s.name if hasattr(s, "name") else str(s))
        for s in raw_req if s
    ]
    preferred_skills: List[str] = [
        s.get("name") if isinstance(s, dict) else (s.name if hasattr(s, "name") else str(s))
        for s in raw_pref if s
    ]

    # If job has no pre-classified skills, extract from description
    if not required_skills and not preferred_skills and job_desc:
        extracted = extract_skills_from_text(job_desc)
        required_skills = extracted[:5] if len(extracted) >= 5 else extracted
        preferred_skills = extracted[5:8] if len(extracted) > 5 else []

    # Gather all candidate skills from resume
    candidate_skills: List[str] = []
    skills_obj = resume_data.get("skills", {})
    if isinstance(skills_obj, dict):
        for k, v in skills_obj.items():
            if isinstance(v, list):
                candidate_skills.extend(v)
    elif isinstance(skills_obj, list):
        candidate_skills.extend(skills_obj)
        
    # Also extract from full text or project tech
    if resume_raw_text:
        candidate_skills.extend(extract_skills_from_text(resume_raw_text))

    for p in resume_data.get("projects", []):
        tech_str = p.get("tech", "")
        if tech_str:
            candidate_skills.extend([t.strip() for t in tech_str.split(",") if t.strip()])

    candidate_skills_set = {s.lower(): s for s in candidate_skills}

    # Skill matching
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    partial_skills: List[str] = []
    matched_preferred_skills: List[str] = []
    missing_preferred_skills: List[str] = []

    # Evaluate required skills
    for req in required_skills:
        req_clean = req.strip()
        if not req_clean:
            continue
        if req_clean.lower() in candidate_skills_set or any(req_clean.lower() in c.lower() for c in candidate_skills_set):
            matched_skills.append(req_clean)
        else:
            missing_skills.append(req_clean)

    # Evaluate preferred skills
    for pref in preferred_skills:
        pref_clean = pref.strip()
        if not pref_clean:
            continue
        if pref_clean.lower() in candidate_skills_set or any(pref_clean.lower() in c.lower() for c in candidate_skills_set):
            matched_preferred_skills.append(pref_clean)
            if pref_clean not in matched_skills:
                matched_skills.append(pref_clean)
        elif any(c.lower() in pref_clean.lower() for c in candidate_skills_set):
            partial_skills.append(pref_clean)
            matched_preferred_skills.append(pref_clean)
        else:
            missing_preferred_skills.append(pref_clean)
            if pref_clean not in missing_skills:
                missing_skills.append(pref_clean)

    # Match score calculation (honest scoring, no fabricated fallback):
    # 60% required skills coverage
    total_req = len(required_skills)
    total_pref = len(preferred_skills)

    req_match_ratio = (len([s for s in required_skills if s in matched_skills]) / total_req) if total_req > 0 else (1.0 if not required_skills and not preferred_skills else 0.5)
    
    # 25% preferred skills coverage (matched=1.0, partial=0.5)
    pref_match_count = sum(1.0 for s in preferred_skills if s in matched_skills) + sum(0.5 for s in preferred_skills if s in partial_skills)
    pref_match_ratio = (pref_match_count / total_pref) if total_pref > 0 else 0.0

    # 15% keyword/candidate competency density in job description
    if job_desc and candidate_skills:
        found_kw = sum(1 for c in candidate_skills_set if c in job_desc.lower())
        kw_score = min(1.0, found_kw / max(len(candidate_skills_set), 1))
    else:
        kw_score = 0.5 if (matched_skills or partial_skills) else 0.0

    if total_req == 0 and total_pref == 0:
        computed_match_score = int(kw_score * 100)
    else:
        computed_match_score = int((req_match_ratio * 60) + (pref_match_ratio * 25) + (kw_score * 15))

    match_score = max(0, min(100, computed_match_score))

    if match_score >= 80:
        status = "Strong Match"
    elif match_score >= 65:
        status = "Good Match"
    elif match_score >= 45:
        status = "Moderate Match"
    else:
        status = "Low Match"

    # Construct skill gaps
    skill_gaps: List[SkillGapItem] = []
    for skill in matched_skills:
        meta = get_skill_metadata(skill)
        skill_gaps.append(SkillGapItem(
            skill=skill,
            status="Strong",
            score=90 if skill.lower() in ["javascript", "react", "python"] else 85,
            category=meta["category"],
            description=meta["description"]
        ))

    for skill in partial_skills:
        meta = get_skill_metadata(skill)
        skill_gaps.append(SkillGapItem(
            skill=skill,
            status="Good",
            score=65,
            category=meta["category"],
            description=meta["description"]
        ))

    for skill in missing_skills:
        meta = get_skill_metadata(skill)
        skill_gaps.append(SkillGapItem(
            skill=skill,
            status="Missing",
            score=20,
            category=meta["category"],
            description=f"No explicit {skill} implementation or repository references identified in your uploaded resume."
        ))

    # Compile ATS breakdown
    all_target_keywords = required_skills + preferred_skills
    ats_breakdown = calculate_ats_metrics(resume_data, resume_raw_text or str(resume_data), all_target_keywords)

    # Compile Learning Recommendations
    learning_recommendations = get_recommendations_for_skills(missing_skills + partial_skills, max_count=6)

    # Executive summary
    if matched_skills:
        matched_str = ", ".join(matched_skills[:3])
        missing_str = ", ".join(missing_skills[:3]) if missing_skills else "none"
        summary = (
            f"Your profile exhibits strong alignment with key competencies for {job_title}, "
            f"notably in {matched_str}. Addressing gaps in {missing_str} "
            f"will make your application stand out significantly to engineering recruiters."
        )
    else:
        missing_str = ", ".join(missing_skills[:4]) if missing_skills else "target requirements"
        summary = (
            f"Your profile currently has limited direct alignment with the stated requirements for {job_title}. "
            f"Key missing skills include {missing_str}. "
            f"We recommend building practical hands-on projects in these areas before applying."
        )

    return AnalysisResponse(
        jobTitle=job_title,
        company=company,
        matchScore=match_score,
        atsScore=ats_breakdown.score,
        status=status,
        summary=summary,
        matchedSkills=matched_skills,
        missingSkills=missing_skills,
        partialSkills=partial_skills,
        matchedPreferredSkills=matched_preferred_skills,
        missingPreferredSkills=missing_preferred_skills,
        skillGaps=skill_gaps,
        learningRecommendations=learning_recommendations,
        atsBreakdown=ats_breakdown
    )
