import asyncio
import io
import os
import sys
from pathlib import Path
from pypdf import PdfWriter
import httpx

# Ensure backend directory is in path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from main import app
from app.database import setup_database, Base

def create_sample_pdf(text_content: str) -> bytes:
    """Generates a valid PDF with extractable text content and Type1 font dictionary."""
    from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
    
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    
    font_dict = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    
    res_dict = DictionaryObject({
        NameObject("/Font"): DictionaryObject({
            NameObject("/F1"): font_dict
        })
    })
    page[NameObject("/Resources")] = writer._add_object(res_dict)
    
    lines = text_content.splitlines()
    stream_content = "BT\n/F1 11 Tf\n50 720 Td\n14 TL\n"
    for line in lines:
        clean_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_content += f"({clean_line}) '\n"
    stream_content += "ET\n"
    
    stream = DecodedStreamObject()
    stream.set_data(stream_content.encode('latin1', 'replace'))
    page[NameObject("/Contents")] = writer._add_object(stream)
    
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()

async def run_tests():
    print("=" * 70)
    print("ResumeMate - Phase 2 Upload & Resume NLP Automated Verification Suite")
    print("=" * 70)
    
    # 1. Initialize database engine for test
    db_engine = await setup_database()
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    results = []

    def record(name, passed, details=""):
        status_str = "PASS" if passed else "FAIL"
        results.append((name, passed, details))
        print(f"[{status_str}] {name}")
        if details:
            print(f"       -> {details}")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        
        # -------------------------------------------------------------
        # Test 1: Valid Text-Based Resume PDF
        # -------------------------------------------------------------
        resume_text = """Alex Rivera
Software Engineer
Email: alex.rivera@example.com
Phone: +1 (555) 234-5678
LinkedIn: linkedin.com/in/alexrivera
GitHub: github.com/alexrivera

Professional Summary
Experienced full-stack software engineer specializing in scalable Python web services and React frontends.

Technical Skills
Languages: Python, JavaScript, TypeScript, SQL, HTML, CSS
Frameworks: FastAPI, React, Node.js, Express
Databases: PostgreSQL, Redis, MongoDB
DevOps: Docker, Git, CI/CD, Linux

Education
Bachelor of Technology in Computer Science & Engineering
State University of Technology
2020 - 2024
CGPA: 8.9 / 10.0

Work Experience
Software Engineer Intern at Apex Technologies
Jun 2023 - Dec 2023
- Built 15+ RESTful API endpoints with FastAPI and asyncpg.
- Optimized query latency by 35% through indexing on PostgreSQL.

Projects
Resume Matcher | Python, React, PostgreSQL
- Developed AI-driven resume parsing and skill matching engine.
- Implemented responsive live resume builder with Tailwind CSS.
"""
        valid_pdf_bytes = create_sample_pdf(resume_text)
        
        resp = await client.post(
            "/api/resumes/upload",
            files={"file": ("Alex_Rivera_Resume.pdf", valid_pdf_bytes, "application/pdf")}
        )
        t1_passed = resp.status_code == 200
        data = resp.json() if t1_passed else {}
        extracted_skills = data.get("parsedData", {}).get("extracted_skills", [])
        has_skills = "Python" in extracted_skills and "React" in extracted_skills
        file_id = data.get("id", "")
        file_path = data.get("filePath", "")
        saved_on_disk = os.path.exists(BACKEND_DIR / file_path) if file_path else False

        record(
            "1. Valid Text-Based Resume PDF Upload & Parse",
            t1_passed and has_skills and saved_on_disk,
            f"Extracted {len(extracted_skills)} skills: {extracted_skills[:6]} | Saved to: {file_path}"
        )

        # -------------------------------------------------------------
        # Test 2: Scanned / Sparse PDF (Graceful OCR Fallback Handling)
        # -------------------------------------------------------------
        sparse_pdf_bytes = create_sample_pdf("Page 1")
        resp = await client.post(
            "/api/resumes/upload",
            files={"file": ("Scanned_Document.pdf", sparse_pdf_bytes, "application/pdf")}
        )
        t2_passed = resp.status_code == 200
        data2 = resp.json() if t2_passed else {}
        status2 = data2.get("status", "")
        record(
            "2. Scanned / Sparse PDF Detection & Safe Fallback",
            t2_passed and status2 in ("needs_ocr", "ready"),
            f"Status: '{status2}', OCR/Status: {data2.get('parsedData', {}).get('ocr_applied')} (no crash)"
        )

        # -------------------------------------------------------------
        # Test 3: Invalid / Non-PDF File (Reject unsupported types)
        # -------------------------------------------------------------
        resp = await client.post(
            "/api/resumes/upload",
            files={"file": ("photo.png", b"\x89PNG\r\n\x1a\nfakeimagebytes", "image/png")}
        )
        record(
            "3. Reject Non-PDF/Non-DOCX Unsupported Files",
            resp.status_code == 400,
            f"Status: {resp.status_code}, Error: {resp.json().get('detail')}"
        )

        # -------------------------------------------------------------
        # Test 4: Empty (0-byte) and Corrupt PDF Handling
        # -------------------------------------------------------------
        resp_empty = await client.post(
            "/api/resumes/upload",
            files={"file": ("empty.pdf", b"", "application/pdf")}
        )
        
        resp_corrupt = await client.post(
            "/api/resumes/upload",
            files={"file": ("corrupt.pdf", b"%PDF-ThisIsBrokenCorruptData12345", "application/pdf")}
        )
        t4_passed = resp_empty.status_code == 400 and resp_corrupt.status_code == 400
        record(
            "4. Reject Empty (0-byte) and Corrupt PDFs",
            t4_passed,
            f"Empty HTTP {resp_empty.status_code} ({resp_empty.json().get('detail')}) | Corrupt HTTP {resp_corrupt.status_code}"
        )

        # -------------------------------------------------------------
        # Test 5: Resume with Missing Sections (Handles Gracefully without Fake Data)
        # -------------------------------------------------------------
        minimal_text = """Jane Doe
Email: jane.doe@tech.io
Phone: 555-0100

Technical Skills
Python, SQL, Git

Education
Bachelor of Science
State College
2023
"""
        minimal_pdf_bytes = create_sample_pdf(minimal_text)
        resp = await client.post(
            "/api/resumes/upload",
            files={"file": ("Jane_Doe_Minimal.pdf", minimal_pdf_bytes, "application/pdf")}
        )
        t5_passed = resp.status_code == 200
        data5 = resp.json() if t5_passed else {}
        exp5 = data5.get("parsedData", {}).get("experience", [])
        proj5 = data5.get("parsedData", {}).get("projects", [])
        # Should NOT invent mock companies or mock projects!
        no_fake_data = len(exp5) == 0 and len(proj5) == 0
        record(
            "5. Resume with Missing Sections (No Invented Mock Data)",
            t5_passed and no_fake_data,
            f"Experience count: {len(exp5)} (expected 0) | Projects count: {len(proj5)} (expected 0)"
        )

        # -------------------------------------------------------------
        # Test 6: Database Persistence and Retrieval via API
        # -------------------------------------------------------------
        resp_get = await client.get(f"/api/resumes/files/{file_id}")
        t6_passed = resp_get.status_code == 200
        get_data = resp_get.json() if t6_passed else {}
        retrieved_id_match = get_data.get("id") == file_id
        record(
            "6. Database Persistence & Retrieval (GET /api/resumes/files/{id})",
            t6_passed and retrieved_id_match,
            f"Retrieved stored record ID: {get_data.get('id')} with filename '{get_data.get('name')}'"
        )

        # -------------------------------------------------------------
        # Test 7: Duplicate Processing & Error Isolation
        # -------------------------------------------------------------
        resp_dup = await client.post(
            "/api/resumes/upload",
            files={"file": ("Alex_Rivera_Resume.pdf", valid_pdf_bytes, "application/pdf")}
        )
        t7_passed = resp_dup.status_code == 200
        dup_data = resp_dup.json() if t7_passed else {}
        unique_id_created = dup_data.get("id") != file_id
        record(
            "7. Duplicate Processing (High-Entropy ID & Isolated Storage)",
            t7_passed and unique_id_created,
            f"Original ID: {file_id} | Duplicate ID: {dup_data.get('id')}"
        )

        # -------------------------------------------------------------
        # Test 8: Frontend-to-Backend Contract Compatibility
        # -------------------------------------------------------------
        required_keys = ["id", "name", "size", "type", "uploadedAt", "status", "extractedText", "parsedData", "filePath"]
        t8_passed = all(k in data for k in required_keys)
        parsed_keys = ["personalInfo", "skills", "education", "experience", "projects", "extracted_skills"]
        t8_passed = t8_passed and all(k in data.get("parsedData", {}) for k in parsed_keys)
        record(
            "8. Frontend React Contract Compatibility (AppContext & ResumeUpload)",
            t8_passed,
            f"All expected frontend response keys verified: {required_keys}"
        )

    print("-" * 70)
    passed_count = sum(1 for _, p, _ in results if p)
    print(f"Total Test Cases: {len(results)} | Passed: {passed_count} | Failed: {len(results) - passed_count}")
    print("=" * 70)
    
    if passed_count == len(results):
        print("ALL PHASE 2 RESUME UPLOAD & PARSING TESTS PASSED SUCCESSFULLY!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_tests())
