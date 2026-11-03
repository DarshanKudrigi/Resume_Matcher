import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("resumemate.lightweight_extractor")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}

MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB max response size

@dataclass
class RawExtractedContent:
    title: str = ""
    company: str = ""
    location: str = ""
    employment_type: str = ""
    visible_text: str = ""
    meta_description: str = ""
    json_ld: Optional[Dict[str, Any]] = None
    source_platform: str = ""
    source_url: str = ""
    extraction_method: str = "http"  # "http" | "playwright" | "agent"
    success: bool = True
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

def _parse_html_content(html: str, url: str, platform: str) -> RawExtractedContent:
    """Extracts title, metadata, JSON-LD, and clean visible text from HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    result = RawExtractedContent(source_url=url, source_platform=platform)

    # 1. JSON-LD Structured Job Data
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            raw_txt = script.string or script.text or ""
            if not raw_txt.strip():
                continue
            parsed = json.loads(raw_txt.strip())
            items = parsed if isinstance(parsed, list) else (parsed.get("@graph", [parsed]) if isinstance(parsed, dict) else [parsed])
            for it in items:
                if isinstance(it, dict) and str(it.get("@type", "")).lower() in ("jobposting", "job_posting"):
                    result.json_ld = it
                    result.title = str(it.get("title", "")).strip()
                    
                    hiring = it.get("hiringOrganization")
                    if isinstance(hiring, dict):
                        result.company = str(hiring.get("name", "")).strip()
                    elif isinstance(hiring, str):
                        result.company = hiring.strip()

                    loc = it.get("jobLocation")
                    if isinstance(loc, dict):
                        addr = loc.get("address", {})
                        if isinstance(addr, dict):
                            parts = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
                            result.location = ", ".join([str(p) for p in parts if p])
                    
                    emp = it.get("employmentType")
                    if isinstance(emp, str):
                        result.employment_type = emp
                    elif isinstance(emp, list):
                        result.employment_type = ", ".join([str(e) for e in emp])
                    break
            if result.json_ld:
                break
        except Exception:
            continue

    # 2. Page Title & Meta Tags
    if not result.title:
        og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
        if og_title and og_title.get("content"):
            result.title = og_title["content"].strip()
        elif soup.title and soup.title.string:
            result.title = soup.title.string.strip()

    og_site = soup.find("meta", property="og:site_name") or soup.find("meta", attrs={"name": "author"})
    if og_site and og_site.get("content") and not result.company:
        result.company = og_site["content"].strip()

    meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
    if meta_desc and meta_desc.get("content"):
        result.meta_description = meta_desc["content"].strip()

    # 3. Clean Visible Text
    for el in soup(["script", "style", "noscript", "nav", "footer", "header", "svg", "button", "input", "form"]):
        el.decompose()

    # Prioritize candidate containers that actually contain meaningful text (> 100 chars)
    candidate_selectors = [
        lambda s: s.find(id="job-detail"),
        lambda s: s.find(class_=re.compile(r'(?:job-detail|job-description|jobDescription|posting-description|jd-description|job_description)', re.I)),
        lambda s: s.find("article"),
        lambda s: s.find("main"),
        lambda s: s.find(id=re.compile(r'(?:job-description|jobDescription|content|main-content)', re.I)),
        lambda s: s.body,
        lambda s: s
    ]

    selected_text = ""
    for sel_fn in candidate_selectors:
        container = sel_fn(soup)
        if container:
            txt = container.get_text(separator="\n", strip=True)
            if len(txt) > 100:
                selected_text = txt
                break

    if not selected_text:
        selected_text = (soup.body or soup).get_text(separator="\n", strip=True)

    cleaned_text = re.sub(r'\n{3,}', '\n\n', selected_text)
    result.visible_text = cleaned_text

    return result

async def extract_via_http(url: str, platform: str) -> RawExtractedContent:
    """Attempts lightweight HTTP extraction."""
    try:
        async with httpx.AsyncClient(
            headers=HEADERS,
            timeout=12.0,
            follow_redirects=True,
            verify=False
        ) as client:
            resp = await client.get(url)

            if resp.status_code == 404:
                return RawExtractedContent(
                    source_url=url,
                    source_platform=platform,
                    success=False,
                    error_message=f"Job posting was not found (HTTP 404) at {platform}."
                )
            if resp.status_code in (401, 403):
                return RawExtractedContent(
                    source_url=url,
                    source_platform=platform,
                    success=False,
                    error_message=f"Access denied (HTTP {resp.status_code}) by {platform}. Login or anti-bot verification required."
                )
            if resp.status_code >= 400:
                return RawExtractedContent(
                    source_url=url,
                    source_platform=platform,
                    success=False,
                    error_message=f"HTTP request failed with status code {resp.status_code} from {platform}."
                )

            if len(resp.content) > MAX_RESPONSE_BYTES:
                return RawExtractedContent(
                    source_url=url,
                    source_platform=platform,
                    success=False,
                    error_message="Webpage content exceeds maximum allowed size limit (5 MB)."
                )

            parsed = _parse_html_content(resp.text, url, platform)
            parsed.extraction_method = "http"
            return parsed

    except httpx.TimeoutException:
        return RawExtractedContent(
            source_url=url,
            source_platform=platform,
            success=False,
            error_message=f"HTTP request timed out after 12 seconds connecting to {platform}."
        )
    except Exception as e:
        logger.warning(f"HTTP extraction error for {url}: {e}")
        return RawExtractedContent(
            source_url=url,
            source_platform=platform,
            success=False,
            error_message=f"HTTP extraction error: {str(e)}"
        )

def _extract_via_playwright_sync(url: str, platform: str) -> RawExtractedContent:
    """Executes browser rendering using Playwright as fallback for dynamic SPAs."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 800},
                ignore_https_errors=True
            )
            page = context.new_page()
            
            # Abort heavy media
            page.route(
                "**/*.{png,jpg,jpeg,gif,webp,svg,mp4,avi,woff,woff2,ttf,eot}",
                lambda route: route.abort()
            )

            try:
                resp = page.goto(url, timeout=20000, wait_until="networkidle")
            except Exception:
                resp = page.goto(url, timeout=20000, wait_until="domcontentloaded")
                try:
                    page.wait_for_selector("#job-detail, main, article, .job-description, .description, [class*='description']", timeout=6000)
                except Exception:
                    page.wait_for_timeout(1500)

            if resp and resp.status == 404:
                return RawExtractedContent(
                    source_url=url,
                    source_platform=platform,
                    success=False,
                    error_message=f"Job posting was not found (HTTP 404) at {platform}."
                )

            html = page.content()
            parsed = _parse_html_content(html, url, platform)
            parsed.extraction_method = "playwright"
            return parsed

        except Exception as e:
            return RawExtractedContent(
                source_url=url,
                source_platform=platform,
                success=False,
                error_message=f"Browser extraction failed: {str(e)}"
            )
        finally:
            if browser:
                try:
                    browser.close()
                except Exception:
                    pass

async def extract_job_content_lightweight(url: str, platform: str) -> RawExtractedContent:
    """
    Tries lightweight HTTP extraction first.
    If text content is insufficient (< 150 chars, indicative of a JS-rendered SPA),
    falls back to controlled Playwright rendering.
    """
    logger.info(f"Attempting lightweight HTTP extraction for {url} ({platform})...")
    http_result = await extract_via_http(url, platform)

    # If HTTP succeeded and captured meaningful content (> 150 chars of visible text)
    if http_result.success and len(http_result.visible_text.strip()) >= 150:
        logger.info(f"HTTP extraction succeeded ({len(http_result.visible_text)} chars).")
        return http_result

    # If blocked by 403 or 401 or not found 404, return directly without running playwright
    if not http_result.success and any(code in (http_result.error_message or "") for code in ["404", "401", "403"]):
        return http_result

    # Fallback to Playwright browser rendering
    logger.info("HTTP text was insufficient; attempting Playwright browser rendering fallback...")
    playwright_result = await asyncio.to_thread(_extract_via_playwright_sync, url, platform)
    
    if playwright_result.success and len(playwright_result.visible_text.strip()) >= 50:
        return playwright_result

    # Return whichever had more content or the error message
    if len(http_result.visible_text) >= len(playwright_result.visible_text):
        return http_result
    return playwright_result
