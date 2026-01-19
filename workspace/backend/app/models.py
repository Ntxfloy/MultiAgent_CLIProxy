from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: Optional[str] = "gpt-5.2-codex"
    history: Optional[List[Message]] = []  # История сообщений

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str # ISO 8601 format string
