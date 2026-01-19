"""
Wrapper для OpenAI клиента, который фиксит баг с None в completion_tokens
"""
from autogen_ext.models.openai import OpenAIChatCompletionClient
from typing import Any, Dict

class SafeOpenAIClient(OpenAIChatCompletionClient):
    """Фиксит баг когда cliProxy возвращает completion_tokens: None"""
    
    async def create(self, *args, **kwargs):
        result = await super().create(*args, **kwargs)
        
        # Фиксим usage если там None
        if hasattr(result, 'usage') and result.usage:
            if result.usage.completion_tokens is None:
                result.usage.completion_tokens = 0
            if result.usage.prompt_tokens is None:
                result.usage.prompt_tokens = 0
                
        return result
