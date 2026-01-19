from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid

from ..models import ChatRequest, ChatResponse
from ..services import ai_service

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Handles chat messages from the frontend and returns AI responses.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    conversation_id = request.conversation_id if request.conversation_id else str(uuid.uuid4())
    model = request.model or "gpt-5.2-codex"
    history = [msg.dict() for msg in request.history] if request.history else []

    ai_response_text = await ai_service.generate_response(
        message=request.message,
        conversation_id=conversation_id,
        model=model,
        history=history
    )
    
    return ChatResponse(
        response=ai_response_text,
        conversation_id=conversation_id,
        timestamp=datetime.now().isoformat()
    )

