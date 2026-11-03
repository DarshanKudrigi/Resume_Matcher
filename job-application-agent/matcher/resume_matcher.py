import json
import os
import re
import time
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    MATCH_THRESHOLD,
    GROQ_MAX_RETRIES,
    GROQ_REQUEST_DELAY,
    GROQ_TPM_LIMIT,
    GROQ_MAX_TOKENS
)
from tracker.models import Job

logger = logging.getLogger("job_application_agent.matcher")

# Persistent and in-memory cache for successfully completed job-matching results
_SCORING_CACHE: Dict[str, dict] = {}
CACHE_FILE = Path(__file__).resolve().parent.parent / ".scoring_cache.json"

def _load_disk_cache() -> None:
    """Load cached scores from disk to avoid rescoring across runs."""
    global _SCORING_CACHE
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    _SCORING_CACHE.update(loaded)
                    logger.info(f"Loaded {len(loaded)} cached job scores from {CACHE_FILE.name}")
        except Exception as e:
            logger.debug(f"Could not load scoring cache from disk: {e}")

def _save_disk_cache() -> None:
    """Save scoring cache to disk."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_SCORING_CACHE, f, indent=2)
    except Exception as e:
        logger.debug(f"Could not save scoring cache to disk: {e}")

# Load cached scores on module initialization
_load_disk_cache()

def _get_cache_key(job: Job, resume_hash: str) -> str:
    """Generate a stable cache key based on job identifier/URL and resume hash."""
    job_id = (job.id or job.url or f"{job.title}@{job.company}").strip().lower()
    return f"{job_id}:{resume_hash}"

def get_scoring_cache() -> Dict[str, dict]:
    """Retrieve the current in-memory scoring cache."""
    return _SCORING_CACHE

def clear_scoring_cache() -> None:
    """Clear all cached scoring entries from memory and disk."""
    global _SCORING_CACHE
    _SCORING_CACHE.clear()
    if CACHE_FILE.exists():
        try:
            CACHE_FILE.unlink()
        except Exception:
            pass


class TokenUsageTracker:
    """Sliding 60-second window token tracker to guarantee requests stay within Groq TPM limit."""
    
    def __init__(self, tpm_limit: int = 8000, safety_buffer: int = 1000):
        self.tpm_limit = tpm_limit
        self.effective_limit = max(1000, tpm_limit - safety_buffer)
        # List of (timestamp, tokens_consumed)
        self.history: List[Tuple[float, int]] = []

    def _purge_old_entries(self, now: float) -> None:
        cutoff = now - 60.0
        self.history = [entry for entry in self.history if entry[0] > cutoff]

    def get_used_tokens_last_minute(self, now: float) -> int:
        self._purge_old_entries(now)
        return sum(tokens for _, tokens in self.history)

    def wait_for_tpm_budget(self, estimated_tokens: int) -> float:
        """Checks if estimated_tokens would breach TPM limit.
        If yes, sleeps until older tokens expire from the 60s sliding window.
        Returns total seconds waited.
        """
        total_waited = 0.0
        while True:
            now = time.time()
            self._purge_old_entries(now)
            used = sum(tokens for _, tokens in self.history)
            
            if (used + estimated_tokens) <= self.effective_limit or not self.history:
                # Within TPM budget
                return total_waited
            
            # Find earliest entry that needs to expire
            oldest_ts, _ = self.history[0]
            sleep_needed = max(1.0, (oldest_ts + 60.0) - now + 0.5)
            logger.info(
                f"[TPM Throttling] Rolling 60s usage: {used} tokens. Upcoming request requires ~{estimated_tokens} tokens "
                f"(limit {self.effective_limit}). Waiting {sleep_needed:.1f}s for budget replenishment..."
            )
            print(
                f"  [TPM Throttling] Token budget nearly full ({used}/{self.effective_limit} TPM). "
                f"Pausing {sleep_needed:.1f}s to prevent 429 rate limit..."
            )
            time.sleep(sleep_needed)
            total_waited += sleep_needed

    def record_usage(self, tokens: int) -> None:
        """Record tokens consumed at current timestamp."""
        now = time.time()
        self._purge_old_entries(now)
        self.history.append((now, max(1, tokens)))


# Global sliding-window tracker initialized with config TPM limit
_token_tracker = TokenUsageTracker(
    tpm_limit=GROQ_TPM_LIMIT or 8000,
    safety_buffer=1000
)


def _extract_retry_after(err: Exception) -> Optional[float]:
    """Extract Retry-After duration in seconds from response headers or error messages."""
    # 1. From response headers (HTTP 429 Retry-After)
    try:
        resp = getattr(err, "response", None)
        if resp is not None:
            headers = getattr(resp, "headers", {})
            header_val = headers.get("retry-after") or headers.get("Retry-After")
            if header_val:
                try:
                    return float(header_val)
                except (ValueError, TypeError):
                    pass
    except Exception:
        pass

    # 2. From error message text regex (e.g. "try again in 2.5s" or "try again in 1400ms")
    try:
        msg = str(err)
        m_sec = re.search(r"try again in ([0-9.]+)\s*s", msg, re.IGNORECASE)
        if m_sec:
            return float(m_sec.group(1))
        m_ms = re.search(r"try again in ([0-9.]+)\s*ms", msg, re.IGNORECASE)
        if m_ms:
            return float(m_ms.group(1)) / 1000.0
    except Exception:
        pass

    return None


def compress_resume_for_matching(resume_text: str, max_chars: int = 1500) -> str:
    """Extract and compact key resume sections (skills, experience, education).
    Strips noise, personal identifiers, contact info, and filler text to minimize token usage.
    """
    if not resume_text:
        return ""
    
    text = resume_text.strip()
    # Remove emails, URLs, phone numbers, and address strings
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '', text)
    
    # Remove common filler phrases / disclaimers
    text = re.sub(r'(?i)(references available upon request|curriculum vitae|resume|declaration|i hereby declare.*?)\b', '', text)
    
    # Normalize excessive newlines and whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Keywords indicating essential matching content
    priority_keywords = (
        "skill", "python", "java", "javascript", "react", "node", "sql", "aws", "azure", "gcp",
        "docker", "kubernetes", "fastapi", "django", "express", "mongodb", "postgresql",
        "experience", "engineer", "developer", "project", "education", "degree", "bachelor",
        "master", "b.tech", "m.tech", "framework", "database", "api", "git", "ci/cd"
    )
    
    cleaned_full = "\n".join(lines)
    if len(cleaned_full) <= max_chars:
        return cleaned_full

    # Select lines with priority keywords or short section headers
    selected = []
    current_len = 0
    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in priority_keywords) or len(line) < 80:
            if current_len + len(line) + 1 <= max_chars:
                selected.append(line)
                current_len += len(line) + 1
            else:
                break
    
    result = "\n".join(selected) if selected else cleaned_full[:max_chars]
    return result.strip()


def clean_and_truncate_jd(jd_text: str, max_chars: int = 1800) -> str:
    """Strip standard boilerplate sections (EEO, benefits, company culture, disclaimers)
    and truncate the job description to essential requirements and qualifications.
    """
    if not jd_text:
        return ""
    
    text = jd_text.strip()
    
    # Strip URL links and emails
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', text)
    
    # Remove boilerplate blocks common in job postings
    boilerplate_patterns = [
        r'(?i)(equal opportunity employer|eeo statement|we are committed to equal|diversity & inclusion).*?(?=\n\n|\Z)',
        r'(?i)(benefits\s*(?:&|and)?\s*perks|what we offer|our benefits|perks\s*:).*?(?=\n\n|\Z)',
        r'(?i)(about (our company|us|the team)|who we are|company overview).*?(?=\n\n|role|responsibilities|requirements|\Z)',
        r'(?i)(physical demands|working conditions|reasonable accommodations).*?(?=\n\n|\Z)',
        r'(?i)(notice to (recruiters|agencies|staffing)|third[- ]?party agencies).*?(?=\n\n|\Z)',
        r'(?i)(covid-19 vaccination|vaccine requirement).*?(?=\n\n|\Z)',
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
        
    # Normalize whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    text = text.strip()
    
    if len(text) <= max_chars:
        return text
        
    # Truncate at natural break
    truncated = text[:max_chars]
    last_break = max(truncated.rfind('\n'), truncated.rfind('. '), truncated.rfind('; '))
    if last_break > int(max_chars * 0.7):
        truncated = truncated[:last_break]
    return truncated.strip()


# Support official Groq SDK with graceful fallback to OpenAI-compatible client
try:
    from groq import (
        Groq,
        AuthenticationError as GroqAuthError,
        NotFoundError as GroqNotFoundError,
        RateLimitError as GroqRateLimitError,
        BadRequestError as GroqBadRequestError
    )
    _GROQ_SDK_AVAILABLE = True
except ImportError:
    _GROQ_SDK_AVAILABLE = False
    from openai import (
        OpenAI,
        AuthenticationError as GroqAuthError,
        NotFoundError as GroqNotFoundError,
        RateLimitError as GroqRateLimitError,
        BadRequestError as GroqBadRequestError
    )

# Compact, token-efficient prompt preserving the exact JSON schema and scoring criteria
SCORE_PROMPT = """You are a recruitment expert. Evaluate candidate resume vs job description.
Return ONLY valid JSON matching this schema:
{{
  "score": 0.0,
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "recommendation": "apply",
  "reason": "one sentence explaining score",
  "experience_required": 0,
  "experience_match": true
}}

Rules:
- score: float 0.0 to 1.0 based on technical and skill match
- recommendation: "apply" (score>=0.75), "maybe" (0.50-0.74), or "skip" (<0.50)
- experience_required: minimum years required extracted from JD (0 for fresher/0-2 yrs or unspecified, max 20)
- experience_match: true if experience_required <= 2, else false

RESUME:
{resume}

JOB DESCRIPTION:
{jd}"""

_client = None

def get_client():
    """Initializes and returns the Groq client.
    Note: max_retries=0 ensures the SDK does NOT perform overlapping hidden retries,
    allowing our single controlled retry loop to manage backoff and token limits.
    """
    global _client
    if _client is not None:
        return _client

    api_key = (GROQ_API_KEY or os.getenv("GROQ_API_KEY") or "").strip()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured. Please set GROQ_API_KEY in your .env file or environment variables."
        )

    if _GROQ_SDK_AVAILABLE:
        # Disable internal SDK retries to prevent overlapping retry loops
        _client = Groq(api_key=api_key, max_retries=0)
    else:
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            max_retries=0,
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

    if "experience_match" not in data:
        data["experience_match"] = data["experience_required"] <= 2

    return data


def score_job(job: Job, resume_text: str, max_retries: Optional[int] = None) -> Job:
    """Score a single job against the candidate's resume using Groq LLM.
    
    Includes:
      - Prompt compaction (resume compression + JD boilerplate stripping).
      - Strict max_tokens=350 to prevent huge token allocation.
      - Token-aware sliding-window throttling (TPM budget protection).
      - Single retry loop with exponential backoff and Retry-After header inspection.
      - In-memory and on-disk persistent caching by stable job ID & resume hash.
      - Safe failure isolation without stopping other jobs.
    """
    retries_limit = max(1, min(max_retries or GROQ_MAX_RETRIES or 3, 5))
    
    # 1. Compress resume and generate cache key
    compressed_resume = compress_resume_for_matching(resume_text, max_chars=1500)
    resume_hash = hashlib.sha256(compressed_resume.encode("utf-8")).hexdigest()[:16]
    cache_key = _get_cache_key(job, resume_hash)
    
    # 2. Check cache first — 0 API calls, 0 token consumption
    if cache_key in _SCORING_CACHE:
        cached = _SCORING_CACHE[cache_key]
        job.match_score = cached["score"]
        job.match_meta = cached
        job.scored = True
        job.scoring_error = None
        return job

    try:
        client = get_client()
    except Exception as e:
        error_msg = f"Initialization error: {e}"
        print(f"  [ERROR] Scoring skipped for '{job.title}' at '{job.company}': {error_msg}")
        job.match_score = 0.5
        job.match_meta = {"matched_skills": [], "missing_skills": [], "recommendation": "maybe", "reason": error_msg}
        job.scored = False
        job.scoring_error = error_msg
        return job

    # 3. Clean and truncate job description to remove boilerplate
    cleaned_jd = clean_and_truncate_jd(job.description or f"{job.title} at {job.company}", max_chars=1800)
    prompt = SCORE_PROMPT.format(resume=compressed_resume, jd=cleaned_jd)

    # 4. Estimate token count and wait for TPM budget if necessary
    output_tokens_limit = GROQ_MAX_TOKENS or 600
    estimated_request_tokens = (len(prompt) // 4) + output_tokens_limit

    candidate_models = [
        GROQ_MODEL or "openai/gpt-oss-120b",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b"
    ]
    models_to_try = list(dict.fromkeys(candidate_models))

    last_error = None
    for model_name in models_to_try:
        for attempt in range(retries_limit):
            try:
                # Sliding-window TPM throttling: pause if token budget is near limit
                _token_tracker.wait_for_tpm_budget(estimated_request_tokens)

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                    max_tokens=output_tokens_limit,
                )
                
                # Record consumed tokens into sliding-window tracker
                total_used = getattr(getattr(response, "usage", None), "total_tokens", None)
                _token_tracker.record_usage(total_used or estimated_request_tokens)

                raw = response.choices[0].message.content or ""
                parsed = _parse_and_validate_scoring(raw)

                job.match_score = parsed["score"]
                job.match_meta = parsed
                job.scored = True
                job.scoring_error = None
                
                # Cache successful scoring result (memory + disk)
                _SCORING_CACHE[cache_key] = parsed
                _save_disk_cache()
                return job

            except (GroqAuthError,) as e:
                last_error = f"Authentication failed: Check your GROQ_API_KEY in .env ({e})"
                print(f"  [FATAL] Groq auth error for '{job.title}' at '{job.company}': {last_error}")
                break  # Fatal: do not retry

            except (GroqNotFoundError,) as e:
                last_error = f"Model '{model_name}' not found ({e}). Trying next fallback model..."
                print(f"  [WARN] Groq model '{model_name}' unavailable (404). Attempting fallback...")
                break  # Try next candidate model

            except (GroqBadRequestError,) as e:
                err_str = str(e).lower()
                if "model_decommissioned" in err_str or "decommissioned" in err_str or "not found" in err_str or "invalid_model" in err_str:
                    last_error = f"Model '{model_name}' decommissioned or invalid ({e}). Trying next fallback model..."
                    print(f"  [WARN] Groq model '{model_name}' decommissioned (400). Attempting fallback...")
                    break
                last_error = f"Bad request for model '{model_name}': {e}"
                print(f"  [WARN] Bad request on attempt {attempt + 1}/{retries_limit} for '{job.title}': {last_error}")
                time.sleep(1.0)

            except (GroqRateLimitError,) as e:
                retry_after = _extract_retry_after(e)
                if retry_after is not None and retry_after > 0:
                    wait_time = max(retry_after, 1.0) + 1.0
                else:
                    wait_time = min(30.0, (2 ** attempt) * 3.0)  # 3.0s, 6.0s, 12.0s exponential backoff
                
                # Signal tracker that limit was encountered
                _token_tracker.record_usage(_token_tracker.effective_limit)

                last_error = f"Rate limited (HTTP 429): {e}. Retrying after {wait_time:.1f}s (attempt {attempt + 1}/{retries_limit})..."
                logger.warning(f"Groq Rate Limit (429) on '{job.title}' with {model_name}: {last_error}")
                print(f"  [WARN 429] Rate limited on '{job.title}'. Waiting {wait_time:.1f}s before retry (attempt {attempt + 1}/{retries_limit})...")
                time.sleep(wait_time)

            except (json.JSONDecodeError, ValueError) as e:
                last_error = f"Malformed response parsing error: {e}"
                print(f"  [WARN] Attempt {attempt + 1}/{retries_limit} invalid response for '{job.title}': {last_error}")
                time.sleep(1.0)

            except Exception as e:
                err_str = str(e).lower()
                if "model_decommissioned" in err_str or "decommissioned" in err_str or "not_found" in err_str:
                    last_error = f"Model '{model_name}' error ({e}). Trying next fallback model..."
                    print(f"  [WARN] Groq model '{model_name}' decommissioned. Attempting fallback...")
                    break
                
                # Check for 429 inside generic exception
                if "429" in err_str or "too many requests" in err_str or "rate limit" in err_str:
                    retry_after = _extract_retry_after(e)
                    wait_time = (retry_after + 1.0) if retry_after else min(30.0, (2 ** attempt) * 3.0)
                    _token_tracker.record_usage(_token_tracker.effective_limit)
                    last_error = f"Rate limit detected (429): {e}. Retrying after {wait_time:.1f}s..."
                    print(f"  [WARN 429] Rate limit detected. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue

                wait_time = (attempt + 1) * 1.5
                last_error = f"API error ({type(e).__name__}): {e}"
                print(f"  [WARN] Attempt {attempt + 1}/{retries_limit} failed for '{job.title}': {last_error}")
                time.sleep(wait_time)

    # If all attempts failed after max_retries:
    print(f"  [FAILED] Scoring failed for '{job.title}' at '{job.company}': {last_error}")
    job.match_score = 0.5
    job.match_meta = {
        "matched_skills": [],
        "missing_skills": [],
        "recommendation": "maybe",
        "reason": f"Scoring notice: {last_error}"
    }
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

    if failed_scoring > 0:
        print(f"      [Notice] {failed_scoring} job(s) could not be scored due to API errors.")
    if skipped_exp > 0:
        print(f"      [Notice] {skipped_exp} job(s) skipped due to experience requirement (>2 yrs).")
    if below_thresh > 0:
        print(f"      [Notice] {below_thresh} job(s) scored below threshold ({threshold:.0%}).")

    return filtered
