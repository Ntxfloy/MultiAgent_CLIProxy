import httpx
import asyncio
import uuid
from typing import List, Dict

CLIPROXY_URL = "http://127.0.0.1:8317/v1/chat/completions"
CLIPROXY_API_KEY = "test-key-123"

async def generate_response(message: str, conversation_id: str, model: str = "gpt-5.2-codex", history: List[Dict] = None) -> str:
    """
    Sends request to cliProxy with full conversation history and returns AI response.
    """
    try:
        # Формируем историю сообщений с system prompt
        messages = [
            {
                "role": "system",
                "content": "Ты полезный AI ассистент. Форматируй свои ответы используя Markdown: используй заголовки (# ## ###), списки (- или 1.), code blocks (```язык код```), жирный текст (**текст**), курсив (*текст*). Структурируй длинные ответы с заголовками и списками для лучшей читаемости."
            }
        ]
        
        if history:
            for msg in history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Добавляем текущее сообщение
        messages.append({"role": "user", "content": message})
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                CLIPROXY_URL,
                headers={
                    "Authorization": f"Bearer {CLIPROXY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[ERROR {response.status_code}]: {response.text}"
                
    except Exception as e:
        return f"[CONNECTION ERROR]: {str(e)}"
