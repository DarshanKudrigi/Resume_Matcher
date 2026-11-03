import sys
sys.stdout.reconfigure(encoding="utf-8")
from app.services.parser_service import extract_text_from_pdf, parse_resume_content
from app.services.matcher_service import analyze_resume_against_job, calculate_ats_metrics

def run_tests():
    print("=" * 60)
    print("RESUME ATS & MATCHING TEST SUITE")
    print("=" * 60)

    # 1. Test Darshan Kudrigi's resume
    print("\n>>> Testing Darshan's Resume:")
    with open("uploads/file-c089ccba97_darshan_kudrigi_resume__3_.pdf", "rb") as f:
        text, pages, is_ocr, msg = extract_text_from_pdf(f.read())
        darshan = parse_resume_content(text, "darshan.pdf")

    print(f"Name: {darshan['personalInfo']['fullName']}")
    print(f"Experience Count: {len(darshan.get('experience', []))}")
    print(f"Projects Count: {len(darshan.get('projects', []))}")
    for p in darshan.get("projects", []):
        print(f"  * {p['name']} | Tech: {p.get('tech')} | Bullets: {len(p.get('bullets', []))}")
    
    print(f"Initial Parsed ATS Base Score: {darshan.get('atsScore')}%")
    assert darshan.get("atsScore") is not None, "darshan atsScore missing"
    assert len(darshan.get("experience", [])) == 0, "Darshan should have 0 experience (student resume)"
    assert len(darshan.get("projects", [])) == 2, "Darshan should have exactly 2 clean projects"

    # Analyze Darshan against sample job
    frontend_job = {
        "title": "Full Stack Engineer",
        "company": "ScaleTech",
        "description": "Looking for a full stack engineer proficient in React, Node.js, FastAPI, and MongoDB.",
        "requiredSkills": ["React", "FastAPI", "Node.js"],
        "preferredSkills": ["MongoDB", "Redis", "Docker"]
    }
    res_darshan = analyze_resume_against_job(darshan, frontend_job, text)
    print(f"Analyzed Match Score: {res_darshan.matchScore}%")
    print(f"Analyzed ATS Score: {res_darshan.atsScore}% ({res_darshan.atsBreakdown.verdict})")
    print("ATS Checklist Items:")
    for it in res_darshan.atsBreakdown.items:
        print(f"  [{it.passed}] {it.label}: {it.note}")

    assert res_darshan.matchScore > 70, "Darshan should have high match score for Full Stack"
    assert res_darshan.atsScore >= 80, "Darshan should have strong ATS score"

    # 2. Test Chandan Gowda's resume
    print("\n>>> Testing Chandan's Resume:")
    with open("uploads/file-8839bf5f97_chandan_resume_2023.docx.pdf", "rb") as f:
        text, pages, is_ocr, msg = extract_text_from_pdf(f.read())
        chandan = parse_resume_content(text, "chandan.pdf")

    print(f"Name: {chandan['personalInfo']['fullName']}")
    print(f"Experience Count: {len(chandan.get('experience', []))}")
    print(f"Projects Count: {len(chandan.get('projects', []))}")
    print(f"Initial Parsed ATS Base Score: {chandan.get('atsScore')}%")
    assert len(chandan.get("projects", [])) == 0, "Chandan should have 0 fragmented projects"
    assert len(chandan.get("experience", [])) == 4, "Chandan should have 4 experiences"

    # Analyze Chandan against sample job
    res_chandan = analyze_resume_against_job(chandan, frontend_job, text)
    print(f"Analyzed Match Score: {res_chandan.matchScore}%")
    print(f"Analyzed ATS Score: {res_chandan.atsScore}% ({res_chandan.atsBreakdown.verdict})")
    print("ATS Checklist Items:")
    for it in res_chandan.atsBreakdown.items:
        print(f"  [{it.passed}] {it.label}: {it.note}")

    # 3. Clean up scratch test files
    print("\nAll assertions passed successfully!")

if __name__ == "__main__":
    run_tests()

