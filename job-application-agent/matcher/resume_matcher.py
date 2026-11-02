import json
import os
import re
import time
from typing import Optional
from config import GROQ_API_KEY, GROQ_MODEL, MATCH_THRESHOLD
from tracker.models import Job

# Support official Groq SDK with graceful fallback to OpenAI-compatible client
try:
    from groq import Groq, AuthenticationError as GroqAuthError, NotFoundError as GroqNotFoundError, RateLimitError as GroqRateLimitError
    _GROQ_SDK_AVAILABLE = True
except ImportError:
    _GROQ_SDK_AVAILABLE = False
    from openai import OpenAI, AuthenticationError as GroqAuthError, NotFoundError as GroqNotFoundError, RateLimitError as GroqRateLimitError

SCORE_PROMPT = """
You are a recruiting expert. Given a resume and a job description,
return ONLY valid JSON with exactly this shape, no extra text:
{{
  "score": 0.0,
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "recommendation": "apply",
  "reason": "one sentence explaining the score",
  "experience_required": 0,
  "experience_match": true
}}

Rules:
- score must be a float between 0.0 and 1.0
- recommendation must be one of: "apply", "maybe", "skip"
- experience_required: extract the MINIMUM years of experience required from the JD as an integer
  * If fresher / no experience mentioned / 0-2 years → set to 0
  * If 2+ years minimum → set to the exact minimum number
  * If you cannot determine it clearly → set to 0
  * Never return a number above 20
- experience_match: set to true if experience_required <= 2, false otherwise
- Score normally based on skills match regardless of experience

RESUME:
{resume}

JOB DESCRIPTION:
{jd}
"""

_client = None

def get_client():
    global _client
    if _client is not None:
        return _client

    api_key = (GROQ_API_KEY or os.getenv("GROQ_API_KEY") or "").strip()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured. Please set GROQ_API_KEY in your .env file or environment variables."
        )

    if _GROQ_SDK_AVAILABLE:
        _client = Groq(api_key=api_key)
    else:
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
    return _client


def _clean_json_response(raw_text: str) -> str:
    """Strip markdown code block markers and whitespace to extract raw JSON."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _parse_and_validate_scoring(raw_text: str) -> dict:
    """Parse JSON and validate the response structure against required schema."""
    cleaned = _clean_json_response(raw_text)
    data = json.loads(cleaned)

    # Validate score
    raw_score = data.get("score")
    if raw_score is None:
        raise ValueError("Missing 'score' in model response")
    score = float(raw_score)
    if score > 1.0 and score <= 100.0:
        # If model returned a percentage like 85.0 instead of 0.85
        score = score / 100.0
    score = max(0.0, min(1.0, score))
    data["score"] = score

    # Validate recommendation
    rec = str(data.get("recommendation", "")).strip().lower()
    if rec not in {"apply", "maybe", "skip"}:
        if score >= 0.75:
            rec = "apply"
        elif score >= 0.50:
            rec = "maybe"
        else:
            rec = "skip"
    data["recommendation"] = rec

    # Validate skills lists
    if not isinstance(data.get("matched_skills"), list):
        data["matched_skills"] = [str(data.get("matched_skills"))] if data.get("matched_skills") else []
    if not isinstance(data.get("missing_skills"), list):
        data["missing_skills"] = [str(data.get("missing_skills"))] if data.get("missing_skills") else []

    # Validate experience_required
    try:
        data["experience_required"] = int(data.get("experience_required", 0))
    except (ValueError, TypeError):
        data["experience_required"] = 0

    return data


def score_job(job: Job, resume_text: str, max_retries: int = 3) -> Job:
    """Score a single job against the candidate's resume using Groq LLM.
    
    Includes retry with exponential backoff for transient failures, safe JSON
    parsing, and distinguishes scoring failures from valid 0.0 scores.
    """
    try:
        client = get_client()
    except Exception as e:
        error_msg = f"Initialization error: {e}"
        print(f"  [ERROR] Scoring skipped for '{job.title}' at '{job.company}': {error_msg}")
        job.match_score = None
        job.match_meta = {}
        job.scored = False
        job.scoring_error = error_msg
        return job

    model_name = GROQ_MODEL or "openai/gpt-oss-120b"
    prompt = SCORE_PROMPT.format(resume=resume_text, jd=job.description or job.title)

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or ""
            parsed = _parse_and_validate_scoring(raw)

            job.match_score = parsed["score"]
            job.match_meta = parsed
            job.scored = True
            job.scoring_error = None
            return job

        except (GroqAuthError,) as e:
            last_error = f"Authentication failed: Check your GROQ_API_KEY in .env ({e})"
            print(f"  [FATAL] Groq auth error for '{job.title}' at '{job.company}': {last_error}")
            break  # Fatal: do not retry

        except (GroqNotFoundError,) as e:
            last_error = f"Model '{model_name}' not found or no access ({e})"
            print(f"  [FATAL] Groq model error for '{job.title}' at '{job.company}': {last_error}")
            break  # Fatal: do not retry

        except (GroqRateLimitError,) as e:
            wait_time = (2 ** attempt) * 1.5
            last_error = f"Rate limited: {e}. Retrying in {wait_time:.1f}s..."
            print(f"  [WARN] Rate limit on attempt {attempt + 1}/{max_retries} for '{job.title}': {last_error}")
            time.sleep(wait_time)

        except (json.JSONDecodeError, ValueError) as e:
            last_error = f"Malformed response parsing error: {e}"
            print(f"  [WARN] Attempt {attempt + 1}/{max_retries} invalid response for '{job.title}': {last_error}")
            time.sleep(1.0)

        except Exception as e:
            wait_time = (attempt + 1) * 1.0
            last_error = f"API error ({type(e).__name__}): {e}"
            print(f"  [WARN] Attempt {attempt + 1}/{max_retries} failed for '{job.title}': {last_error}")
            time.sleep(wait_time)

    # If all attempts failed
    print(f"  [FAILED] Scoring failed for '{job.title}' at '{job.company}': {last_error}")
    job.match_score = None
    job.match_meta = {}
    job.scored = False
    job.scoring_error = str(last_error)
    return job


def filter_jobs(jobs: list[Job], threshold: float = MATCH_THRESHOLD) -> list[Job]:
    """Filter jobs based on scoring validity, experience requirements, and match threshold."""
    filtered = []
    skipped_exp = 0
    below_thresh = 0
    failed_scoring = 0

    for j in jobs:
        if not j.scored or j.match_score is None:
            failed_scoring += 1
            continue

        exp_req = j.match_meta.get("experience_required", 0)
        if exp_req > 20:
            exp_req = 0
        if exp_req > 2:
            skipped_exp += 1
            print(f"  Skipping (requires {exp_req} yrs): {j.title} at {j.company}")
            continue

        if j.match_score >= threshold:
            filtered.append(j)
        else:
            below_thresh += 1

    total_evaluated = len(jobs) - failed_scoring
    if failed_scoring > 0:
        print(f"      [Notice] {failed_scoring} job(s) could not be scored due to API errors.")
    if skipped_exp > 0:
        print(f"      [Notice] {skipped_exp} job(s) skipped due to experience requirement (>2 yrs).")
    if below_thresh > 0:
        print(f"      [Notice] {below_thresh} job(s) scored below threshold ({threshold:.0%}).")

    return filtered