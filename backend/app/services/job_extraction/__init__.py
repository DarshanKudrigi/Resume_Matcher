"""
Job Extraction Service Package
Combines URL classification, Job Application Agent (Playwright),
Lightweight HTTP/Playwright extraction, and Gemini AI structuring.
"""

from .url_classifier import (
    classify_job_url,
    validate_and_sanitize_url,
    URLCategory,
    detect_platform_name,
)
from .lightweight_extractor import extract_job_content_lightweight, RawExtractedContent
from .gemini_service import (
    call_gemini_structured_extraction,
    GeminiStructuredOutput,
    GeminiSkillItem,
    GeminiConfigurationError,
    GeminiExtractionError,
)
from .job_extraction_service import extract_and_process_job

__all__ = [
    "classify_job_url",
    "validate_and_sanitize_url",
    "URLCategory",
    "detect_platform_name",
    "extract_job_content_lightweight",
    "RawExtractedContent",
    "call_gemini_structured_extraction",
    "GeminiStructuredOutput",
    "GeminiSkillItem",
    "GeminiConfigurationError",
    "GeminiExtractionError",
    "extract_and_process_job",
]
