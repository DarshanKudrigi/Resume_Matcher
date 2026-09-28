from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.chat import (
    ChatMessageRequest, ChatMessageResponse, AISuggestionsResponse
)
from app.services.ai_service import (
    generate_chat_response, get_ai_suggestions_for_builder
)

router = APIRouter(prefix="/chat", tags=["AI Assistant"])

@router.post("", response_model=ChatMessageResponse)
async def chat_with_assistant(req: ChatMessageRequest):
    """Processes interactive AI questions about scores, gaps, and improvements."""
    return await generate_chat_response(
        message=req.message,
        current_job=req.currentJob,
        current_resume=req.currentResume,
        analysis_result=req.analysisResult
    )

@router.get("/suggestions", response_model=AISuggestionsResponse)
async def get_builder_suggestions(role: str = Query("Frontend Developer", description="Target role")):
    """Returns AI suggestions for summaries, bullet points, and projects."""
    return get_ai_suggestions_for_builder(role)
