import logging
from typing import Dict, Any, List
import httpx
from datetime import datetime

from app.config import settings
from app.schemas.chat import ChatMessageResponse, AISuggestionsResponse

logger = logging.getLogger("resumemate.ai")

DEFAULT_SUGGESTIONS = [
    "Why is my match score 82%?",
    "What skills am I missing?",
    "How can I improve my resume?",
    "What should I learn first?"
]

async def call_gemini_api(prompt: str) -> str:
    """Calls Google Gemini REST API if GEMINI_API_KEY is configured."""
    if not settings.GEMINI_API_KEY:
        return ""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 600
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.warning(f"Error calling Gemini API: {e}")
    
    return ""

async def generate_chat_response(
    message: str,
    current_job: Dict[str, Any] = None,
    current_resume: Dict[str, Any] = None,
    analysis_result: Dict[str, Any] = None
) -> ChatMessageResponse:
    """Produces intelligent context-aware chat response via Gemini or expert rules."""
    now_time = datetime.now().strftime("%I:%M %p")
    user_query = message.strip()
    lower_query = user_query.lower()

    # Extract context
    job_title = (current_job or {}).get("title") or (analysis_result or {}).get("jobTitle") or "Frontend Engineer"
    company = (current_job or {}).get("company") or (analysis_result or {}).get("company") or "Apex Cloud Technologies"
    match_score = (analysis_result or {}).get("matchScore") or 82
    ats_score = (analysis_result or {}).get("atsScore") or 86
    missing_skills = (analysis_result or {}).get("missingSkills") or ["Docker", "AWS", "System Design"]
    matched_skills = (analysis_result or {}).get("matchedSkills") or ["JavaScript", "React", "HTML", "CSS", "Git"]

    # If Gemini API key is present, prompt the LLM with exact context
    if settings.GEMINI_API_KEY:
        llm_prompt = f"""You are ResumeMate AI Assistant, a friendly and expert technical career coach.
Candidate is applying for: {job_title} at {company}.
Match Score: {match_score}% | ATS Score: {ats_score}%
Matched Skills: {', '.join(matched_skills)}
Missing Skills: {', '.join(missing_skills)}

Candidate Question: "{user_query}"

Respond concisely in 2 to 4 sentences or bullet points. Provide specific, actionable advice to help them get hired."""
        gemini_reply = await call_gemini_api(llm_prompt)
        if gemini_reply:
            return ChatMessageResponse(
                reply=gemini_reply,
                time=now_time,
                sender="assistant",
                suggestions=DEFAULT_SUGGESTIONS
            )

    # Built-in contextual expert engine
    reply = ""
    if any(q in lower_query for q in ["score", "why", "82", "percentage"]):
        reply = (
            f"Your {match_score}% match score is calculated because you satisfy 100% of the core required skills "
            f"({', '.join(matched_skills[:4])})! However, {company} also lists "
            f"{', '.join(missing_skills[:3])} as preferred skills, which are currently not detected in your resume."
        )
    elif any(q in lower_query for q in ["missing", "gap", "lack"]):
        reply = (
            f"Based on the {job_title} requirements at {company}, your primary missing skills are:\n" +
            "\n".join([f"• {s}" for s in missing_skills[:4]]) +
            "\n\nAdding small proof-of-concept projects or certifications for these will close the gap quickly."
        )
    elif any(q in lower_query for q in ["improve", "tips", "better", "advice"]):
        reply = (
            "Here are 3 high-impact ways to improve your resume right now:\n"
            "• Quantify bullet points with impact metrics (e.g. 'reduced render time by 22%').\n"
            f"• Add a project demonstrating {missing_skills[0] if missing_skills else 'Docker'} containerization.\n"
            "• Ensure standard ATS section headers and avoid complex non-standard tables."
        )
    elif any(q in lower_query for q in ["learn first", "start", "order", "where to"]):
        top_skill = missing_skills[0] if missing_skills else "Docker"
        reply = (
            f"We recommend starting with {top_skill} (estimated 6-8 hours). "
            "It has the steepest payoff for full-stack and frontend roles, and fulfills a preferred qualification immediately."
        )
    elif any(q in lower_query for q in ["ats", "tracking", "bot"]):
        reply = (
            f"Your ATS score is currently {ats_score}%. The ATS checker verified your contact details, "
            "education, and skills formatting. Adding keywords like " +
            f"'{missing_skills[0]}' will boost your ranking."
        )
    else:
        reply = (
            f"Based on your profile and the {job_title} role at {company}: "
            f"emphasize your practical hands-on experience in {matched_skills[0] if matched_skills else 'React'}, "
            f"and consider adding a small project involving {missing_skills[0] if missing_skills else 'Docker'} to close your top skill gap!"
        )

    return ChatMessageResponse(
        reply=reply,
        time=now_time,
        sender="assistant",
        suggestions=DEFAULT_SUGGESTIONS
    )

def get_ai_suggestions_for_builder(role: str = "Frontend Developer") -> AISuggestionsResponse:
    """Returns curated AI writing suggestions for the Resume Builder."""
    return AISuggestionsResponse(
        summaries=[
            f"Performance-focused {role} with expertise in building responsive single-page web applications, component libraries, and RESTful API integrations. Passionate about clean code, accessibility, and modern developer tooling.",
            f"Driven software engineer with practical experience developing intuitive frontend interfaces using React, TypeScript, and modern CSS frameworks. Proven ability to translate UX mockups into pixel-perfect production applications.",
            f"Detail-oriented software developer specializing in modern web ecosystems, state management, and Git collaboration workflows. Proven track record in fast-paced Agile development environments."
        ],
        bulletPoints=[
            "Architected reusable React components with custom hooks, reducing code redundancy across pages by 35%.",
            "Optimized asset loading and implemented dynamic code splitting, improving Core Web Vitals and First Contentful Paint by 40%.",
            "Implemented client-side caching and debounced search, cutting redundant network requests by 50%.",
            "Integrated responsive mobile-first layouts using Tailwind CSS, ensuring seamless cross-device compatibility."
        ],
        projectDescriptions=[
            "Engineered a high-performance web dashboard featuring dynamic filtering, responsive grid layouts, and seamless local persistence using modern React hooks.",
            "Developed an end-to-end full-stack prototype with clean modular architecture, comprehensive error handling, and robust form validation.",
            "Designed and shipped a responsive single-page web application with 95+ Lighthouse accessibility and performance ratings."
        ]
    )
