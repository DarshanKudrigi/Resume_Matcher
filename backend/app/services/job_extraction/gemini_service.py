import json
import logging
import re
from typing import Dict, Any, List, Optional, Union
import httpx
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger("resumemate.gemini_service")

class GeminiSkillItem(BaseModel):
    name: Optional[str] = ""
    skill: Optional[str] = ""
    evidence: Optional[str] = ""
    category: Optional[str] = "Technical Skill"

    def get_name(self) -> str:
        return (self.name or self.skill or "").strip()

class GeminiStructuredOutput(BaseModel):
    title: Optional[str] = ""
    job_title: Optional[str] = ""
    company: Optional[str] = ""
    location: Optional[str] = ""
    employment_type: Optional[str] = None
    experience_requirements: Optional[Any] = Field(default_factory=list)
    education_requirements: Optional[Any] = Field(default_factory=list)
    experience_required: Optional[Any] = None
    education_required: Optional[Any] = None
    required_skills: List[GeminiSkillItem] = Field(default_factory=list)
    preferred_skills: List[GeminiSkillItem] = Field(default_factory=list)
    additional_mentioned_skills: List[GeminiSkillItem] = Field(default_factory=list)
    responsibilities: Optional[Any] = Field(default_factory=list)
    qualifications: Optional[Any] = Field(default_factory=list)
    description_summary: Optional[str] = ""

    def get_title(self) -> str:
        return (self.title or self.job_title or "").strip()

    def get_experience_list(self) -> List[str]:
        items = self.experience_requirements or self.experience_required or []
        if isinstance(items, str):
            return [items] if items.strip() else []
        if isinstance(items, list):
            return [str(i).strip() for i in items if str(i).strip()]
        return []

    def get_education_list(self) -> List[str]:
        items = self.education_requirements or self.education_required or []
        if isinstance(items, str):
            return [items] if items.strip() else []
        if isinstance(items, list):
            return [str(i).strip() for i in items if str(i).strip()]
        return []

    def get_responsibilities_list(self) -> List[str]:
        items = self.responsibilities or []
        if isinstance(items, str):
            return [line.strip("- •*\t") for line in items.splitlines() if line.strip("- •*\t")]
        if isinstance(items, list):
            return [str(i).strip("- •*\t") for i in items if str(i).strip("- •*\t")]
        return []

    def get_qualifications_list(self) -> List[str]:
        items = self.qualifications or []
        if isinstance(items, str):
            return [line.strip("- •*\t") for line in items.splitlines() if line.strip("- •*\t")]
        if isinstance(items, list):
            return [str(i).strip("- •*\t") for i in items if str(i).strip("- •*\t")]
        return []

GEMINI_SYSTEM_PROMPT = """You are an expert technical recruiter and job specification parser.
Your task is to analyze the provided extracted Job Posting content and return ONLY a valid structured JSON object matching the required schema.

STRICT EXTRACTION RULES:
1. Title & Company: Extract the exact job title ("title") and hiring company ("company"). If the company is not mentioned, return "Company not specified".
2. Location & Employment: Extract specific location ("location") and employment type ("employment_type", e.g. Full-time, Part-time, Internship, Contract).
3. Experience & Education: Extract explicit years of experience ("experience_requirements": [...]) and degree requirements ("education_requirements": [...]).
4. SKILL CLASSIFICATION RULES (CRITICAL):
   - required_skills: ONLY skills explicitly stated as mandatory, required, minimum, or essential (e.g. "Must have Python experience", "Strong knowledge of SQL is required").
   - preferred_skills: ONLY skills explicitly described as preferred, desirable, bonus, or nice-to-have (e.g. "Knowledge of AWS is preferred", "Exposure to Docker is beneficial").
   - additional_mentioned_skills: Technologies or tools mentioned in the job description without sufficient evidence to classify as required or preferred (e.g. "Experience with CI/CD is mentioned in passing").
   - Each skill object MUST have: {"name": "SkillName", "evidence": "Exact short sentence from text", "category": "Frontend/Backend/Cloud/etc"}
5. ABSOLUTE PROHIBITIONS:
   - NEVER classify every skill as required.
   - NEVER invent or hallucinate skills not present in the provided text.
   - NEVER add technologies based on the job title alone.
   - NEVER duplicate a skill across multiple categories (each skill must appear in exactly one list).
   - DO NOT treat generic English words (e.g. "Communication", "Teamwork", "Solutions") as technical skills.
6. EVIDENCE: For each extracted skill, provide the exact or near-exact short sentence or phrase from the text as 'evidence'.
7. Responsibilities & Qualifications: Extract concrete bullet points for core responsibilities ("responsibilities") and qualifications ("qualifications").
8. Description Summary: Write a concise 2-3 sentence overview of the role ("description_summary").

Return ONLY the raw JSON object, without markdown formatting or code blocks.
"""

class GeminiExtractionError(Exception):
    """Raised when Gemini API fails or returns invalid structured output."""
    pass

class GeminiConfigurationError(Exception):
    """Raised when GEMINI_API_KEY is not configured."""
    pass

CANDIDATE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.8-flash",
    "gemini-2.5-pro",
]

async def call_gemini_structured_extraction(
    extracted_text: str,
    meta_info: Optional[Dict[str, Any]] = None,
    max_retries: int = 1
) -> GeminiStructuredOutput:
    """
    Sends extracted job content to the Google Gemini API with temperature=0
    and JSON schema enforcement. Validates the output with Pydantic.
    """
    api_key = (settings.GEMINI_API_KEY or "").strip()
    if not api_key:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is not configured in backend/.env. "
            "Please configure your Google Gemini API key to enable AI-powered job extraction."
        )

    # Prepare context payload
    meta_hint = ""
    if meta_info:
        meta_hint = f"\nADDITIONAL METADATA DETECTED:\nTitle: {meta_info.get('title', '')}\nCompany: {meta_info.get('company', '')}\nPlatform: {meta_info.get('platform', '')}\n"

    user_content = f"{meta_hint}\nEXTRACTED JOB DESCRIPTION CONTENT:\n{extracted_text[:12000]}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": GEMINI_SYSTEM_PROMPT},
                    {"text": user_content}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.0,
            "maxOutputTokens": 8192
        }
    }

    last_error: Optional[Exception] = None

    for model_name in CANDIDATE_MODELS:
        endpoint_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(endpoint_url, json=payload)

                    if resp.status_code == 404 or resp.status_code == 503:
                        logger.warning(f"Model {model_name} returned status {resp.status_code}, trying next candidate...")
                        break  # Try next model

                    if resp.status_code == 400:
                        err_json = resp.json()
                        raise GeminiExtractionError(f"Gemini API Bad Request: {err_json.get('error', {}).get('message', resp.text)}")
                    if resp.status_code == 403:
                        raise GeminiExtractionError("Gemini API key is invalid or quota has been exceeded (HTTP 403).")
                    if resp.status_code == 429:
                        raise GeminiExtractionError("Gemini API rate limit exceeded. Please retry in a few moments (HTTP 429).")
                    if resp.status_code >= 500:
                        raise GeminiExtractionError(f"Gemini service temporary error (HTTP {resp.status_code}).")

                    if resp.status_code != 200:
                        raise GeminiExtractionError(f"Gemini API returned unexpected status code {resp.status_code}.")

                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise GeminiExtractionError("Gemini API returned an empty candidate list.")

                    raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    if not raw_text:
                        raise GeminiExtractionError("Gemini API returned empty text content.")

                    # Clean markdown backticks if returned
                    cleaned_json = raw_text
                    if cleaned_json.startswith("```"):
                        cleaned_json = re.sub(r'^```(?:json)?\s*', '', cleaned_json, flags=re.IGNORECASE)
                        cleaned_json = re.sub(r'\s*```$', '', cleaned_json)
                    cleaned_json = cleaned_json.strip()

                    try:
                        parsed_dict = json.loads(cleaned_json)
                    except json.JSONDecodeError as jde:
                        raise GeminiExtractionError(f"Failed to parse Gemini response as JSON: {jde}. Raw: {raw_text[:200]}")

                    structured = GeminiStructuredOutput.model_validate(parsed_dict)
                    return structured

            except (httpx.TimeoutException, httpx.NetworkError) as net_err:
                last_error = GeminiExtractionError(f"Network error contacting Gemini API: {net_err}")
                logger.warning(f"Attempt {attempt + 1} with {model_name} failed: {net_err}")
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} with {model_name} failed: {e}")

    if last_error:
        raise last_error
    raise GeminiExtractionError("All Gemini model candidates failed or timed out.")
