from typing import List, Dict, Optional, Any
from pydantic import BaseModel

class ChatMessageRequest(BaseModel):
    message: str
    currentJob: Optional[Dict[str, Any]] = None
    currentResume: Optional[Dict[str, Any]] = None
    analysisResult: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    reply: str
    time: str
    sender: str = "assistant"
    suggestions: List[str] = []

class AISuggestionsResponse(BaseModel):
    summaries: List[str]
    bulletPoints: List[str]
    projectDescriptions: List[str]
