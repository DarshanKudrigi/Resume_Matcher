from dataclasses import dataclass, field
from typing import Optional
import hashlib

@dataclass
class Job:
    title: str
    company: str
    location: str
    url: str
    description: str
    source: str
    scraped_at: str
    match_score: Optional[float] = None
    status: str = "new"
    match_meta: dict = field(default_factory=dict)
    scored: bool = False
    scoring_error: Optional[str] = None
    id: str = field(init=False)

    def __post_init__(self):
        # Normalize URL to create a stable identifier across query params and trailing slashes
        clean_url = (self.url or "").strip().split("?")[0].split("#")[0].rstrip("/").lower()
        unique_key = clean_url if clean_url else f"{(self.title or '').strip().lower()}|{(self.company or '').strip().lower()}"
        self.id = hashlib.md5(unique_key.encode("utf-8")).hexdigest()[:10]