from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import urllib.parse

@dataclass
class RawJobData:
    title: str = ""
    company: str = ""
    location: str = ""
    experience: str = ""
    employment_type: str = ""
    description: str = ""
    responsibilities: List[str] = field(default_factory=list)
    qualifications: List[str] = field(default_factory=list)
    basic_qualifications_text: str = ""       # Evidence for required skills
    preferred_qualifications_text: str = ""   # Evidence for preferred skills
    raw_sections: Dict[str, str] = field(default_factory=dict)
    source: str = ""
    job_id: str = ""
    url: str = ""
    status: str = "success"                   # "success", "partial", "error"
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    unavailable_fields: List[str] = field(default_factory=list)

class BaseJobStrategy(ABC):
    name: str = "BaseStrategy"

    @abstractmethod
    def can_handle(self, parsed_url: urllib.parse.ParseResult) -> bool:
        """Determines if this strategy supports the given URL."""
        raise NotImplementedError

    @abstractmethod
    def extract(self, page, url: str) -> RawJobData:
        """Extracts structured job information from the Playwright page."""
        raise NotImplementedError

