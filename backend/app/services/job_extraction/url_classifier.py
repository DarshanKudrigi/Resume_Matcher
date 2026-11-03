import ipaddress
import logging
import socket
import urllib.parse
from enum import Enum
from typing import Tuple

logger = logging.getLogger("resumemate.url_classifier")

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

class URLCategory(str, Enum):
    LINKEDIN = "LINKEDIN"
    NAUKRI = "NAUKRI"
    OTHER = "OTHER"

def validate_and_sanitize_url(url: str) -> urllib.parse.ParseResult:
    """
    Validates URL protocol (HTTP/HTTPS only) and checks against SSRF / internal IP targets.
    Raises ValueError with descriptive user-facing message if invalid.
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

    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded authentication credentials are not permitted.")

    hostname = parsed.hostname.lower()

    if hostname in ("localhost", "localhost.localdomain", "127.0.0.1", "::1"):
        raise ValueError("Access to local loopback addresses is prohibited.")

    # DNS check to prevent SSRF against internal network or cloud metadata
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            for blocked_net in BLOCKED_IP_NETWORKS:
                if ip_obj in blocked_net:
                    raise ValueError(f"URL resolves to an internal or private network address ({ip_str}), which is restricted.")
    except socket.gaierror:
        logger.debug(f"DNS check skipped/unreachable for host '{hostname}'.")
    except ValueError:
        raise
    except Exception as e:
        logger.warning(f"DNS resolution warning for {hostname}: {e}")

    return parsed

def detect_platform_name(hostname: str) -> str:
    """Returns human-readable name of platform based on domain."""
    h = hostname.lower()
    if "linkedin.com" in h:
        return "LinkedIn"
    if "naukri.com" in h:
        return "Naukri"
    if "lever.co" in h:
        return "Lever"
    if "amazon.jobs" in h:
        return "Amazon Jobs"
    if "careers.microsoft.com" in h:
        return "Microsoft Careers"
    if "greenhouse.io" in h:
        return "Greenhouse"
    if "myworkdayjobs.com" in h or "workday" in h:
        return "Workday"
    if "ashbyhq.com" in h:
        return "Ashby"
    if "smartrecruiters.com" in h:
        return "SmartRecruiters"
    if "workable.com" in h:
        return "Workable"
    
    # Generic domain fallback
    clean_host = h.replace("www.", "").split(".")[0]
    return clean_host.capitalize()

def classify_job_url(url: str) -> Tuple[URLCategory, str, urllib.parse.ParseResult]:
    """
    Validates URL and classifies it into LINKEDIN, NAUKRI, or OTHER along with the platform name.
    """
    parsed = validate_and_sanitize_url(url)
    hostname = (parsed.hostname or "").lower()
    platform = detect_platform_name(hostname)

    if "linkedin.com" in hostname:
        return URLCategory.LINKEDIN, platform, parsed
    elif "naukri.com" in hostname:
        return URLCategory.NAUKRI, platform, parsed
    else:
        return URLCategory.OTHER, platform, parsed

