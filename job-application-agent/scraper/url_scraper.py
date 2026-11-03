import ipaddress
import logging
import socket
import urllib.parse
from typing import List, Optional
from playwright.sync_api import sync_playwright

from .strategies import (
    BaseJobStrategy,
    RawJobData,
    AmazonStrategy,
    MicrosoftStrategy,
    LeverStrategy,
    LinkedInStrategy,
    NaukriStrategy,
    GenericStrategy,
)

logger = logging.getLogger("resumemate.url_scraper")

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # RFC 1918 Private
    ipaddress.ip_network("172.16.0.0/12"),    # RFC 1918 Private
    ipaddress.ip_network("192.168.0.0/16"),   # RFC 1918 Private
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local / Cloud metadata (169.254.169.254)
    ipaddress.ip_network("0.0.0.0/8"),        # This host
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
]

def validate_and_sanitize_url(url: str) -> urllib.parse.ParseResult:
    """
    Validates the URL for protocol compliance and SSRF / internal IP boundaries.
    Raises ValueError with a user-friendly message if invalid.
    """
    if not url or not isinstance(url, str):
        raise ValueError("Job URL must be a non-empty string.")

    cleaned_url = url.strip()
    if not cleaned_url.startswith(("http://", "https://")):
        cleaned_url = f"https://{cleaned_url}"
    try:
        parsed = urllib.parse.urlparse(cleaned_url)
    except Exception as e:
        raise ValueError(f"Malformed URL: {e}")

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Invalid URL protocol. Only HTTP and HTTPS URLs are accepted.")

    if not parsed.hostname:
        raise ValueError("URL must include a valid hostname.")

    # Reject embedded user:pass credentials in URL
    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded authentication credentials are not permitted.")

    hostname = parsed.hostname.lower()

    # Block localhost explicitly
    if hostname in ("localhost", "localhost.localdomain", "127.0.0.1", "::1"):
        raise ValueError("Access to local loopback addresses is prohibited.")

    # DNS resolution validation to prevent SSRF against private networks / metadata
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            for blocked_net in BLOCKED_IP_NETWORKS:
                if ip_obj in blocked_net:
                    raise ValueError(f"URL resolves to an internal or private network address ({ip_str}), which is restricted.")
    except socket.gaierror:
        # If running offline or sandbox without DNS, allow page navigation to surface the network error
        logger.debug(f"DNS check skipped/unreachable for host '{hostname}'.")
    except ValueError:
        raise
    except Exception as e:
        logger.warning(f"DNS check warning for {hostname}: {e}")

    return parsed

class IndividualJobScraper:
    """
    Modular scraper for extracting individual job postings.
    Uses the Strategy pattern to select the appropriate parser based on domain.
    """
    def __init__(self, headless: bool = True, timeout_ms: int = 30000):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.strategies: List[BaseJobStrategy] = [
            AmazonStrategy(),
            MicrosoftStrategy(),
            LeverStrategy(),
            LinkedInStrategy(),
            NaukriStrategy(),
            GenericStrategy(),  # Default fallback
        ]

    def select_strategy(self, parsed_url: urllib.parse.ParseResult) -> BaseJobStrategy:
        for strat in self.strategies:
            if strat.can_handle(parsed_url):
                return strat
        return GenericStrategy()

    def scrape_url(self, url: str) -> RawJobData:
        """
        Executes URL validation, domain detection, Playwright browser navigation,
        and strategy-specific extraction.
        """
        try:
            parsed_url = validate_and_sanitize_url(url)
        except ValueError as ve:
            return RawJobData(
                url=url,
                status="error",
                error_message=str(ve)
            )

        strategy = self.select_strategy(parsed_url)
        logger.info(f"Selected strategy '{strategy.name}' for URL: {url}")

        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(
                    headless=self.headless,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage"
                    ]
                )
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                    ignore_https_errors=True
                )

                # Filter out heavy non-essential media to boost speed while keeping scripts
                page = context.new_page()
                page.route(
                    "**/*.{png,jpg,jpeg,gif,webp,svg,mp4,avi,woff,woff2,ttf,eot}",
                    lambda route: route.abort()
                )

                response = None
                try:
                    response = page.goto(
                        url,
                        timeout=self.timeout_ms,
                        wait_until="domcontentloaded"
                    )
                except Exception as e:
                    err_text = str(e)
                    if "Timeout" in err_text:
                        return RawJobData(
                            url=url,
                            status="error",
                            error_message=f"Navigation timed out after {self.timeout_ms/1000:.0f} seconds while opening {parsed_url.hostname}."
                        )
                    return RawJobData(
                        url=url,
                        status="error",
                        error_message=f"Failed to load job posting: {err_text}"
                    )

                if response and response.status >= 400:
                    if response.status == 404:
                        return RawJobData(
                            url=url,
                            status="error",
                            error_message=f"Job posting was not found (HTTP 404) on {parsed_url.hostname}."
                        )
                    if response.status in (401, 403):
                        return RawJobData(
                            url=url,
                            status="error",
                            error_message=f"Access denied (HTTP {response.status}) by {parsed_url.hostname}. Authentication or bot protection active."
                        )

                # Execute domain strategy
                raw_data = strategy.extract(page, url)
                return raw_data

            except Exception as e:
                logger.error(f"Unexpected error scraping {url}: {e}", exc_info=True)
                return RawJobData(
                    url=url,
                    status="error",
                    error_message=f"Unexpected extraction failure: {str(e)}"
                )
            finally:
                if browser:
                    try:
                        browser.close()
                    except Exception:
                        pass
