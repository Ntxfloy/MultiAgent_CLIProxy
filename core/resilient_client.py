"""
Умный клиент с автоматическим fallback на резервные модели
"""
from autogen_ext.models.openai import OpenAIChatCompletionClient
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Иерархия моделей: от лучших к запасным
MODEL_FALLBACK_CHAINS = {
    "premium": [
        # OpenAI топ
        "gpt-5.2-codex",
        "gpt-5.1-codex",
        "gpt-5.2",
        "gpt-5.1",
        # Kiro топ
        "kiro-claude-opus-4-5-agentic",
        "kiro-claude-sonnet-4-5-agentic",
        "kiro-claude-opus-4-5",
        # Antigravity топ
        "gemini-claude-opus-4-5-thinking",
        "gemini-claude-sonnet-4-5-thinking",
        "gemini-claude-sonnet-4-5",
        # Google топ
        "gemini-3-pro-preview",
        "gemini-2.5-pro"
    ],
    "standard": [
        # Средние модели
        "gemini-2.5-pro",
        "kiro-claude-sonnet-4-5",
        "kiro-claude-sonnet-4",
        "gpt-5.1-codex-mini",
        "gemini-3-flash-preview",
        "gemini-2.5-flash",
        "gpt-5-codex-mini"
    ],
    "fast": [
        # Быстрые и дешевые
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3-flash-preview",
        "tab_flash_lite_preview",
        "gpt-5-codex-mini",
        "gpt-5.1-codex-mini",
        "kiro-claude-haiku-4-5"
    ]
}

class ResilientClient:
    """
    Клиент с автоматическим переключением на резервные модели при ошибках
    """
    
    def __init__(self, model_tier: str, base_url: str, api_key: str, max_retries: int = 3):
        self.model_tier = model_tier
        self.base_url = base_url
        self.api_key = api_key
        self.max_retries = max_retries
        
        # Получаем цепочку fallback моделей
        self.fallback_chain = MODEL_FALLBACK_CHAINS.get(model_tier, MODEL_FALLBACK_CHAINS["standard"])
        self.current_model_index = 0
        
        # Добавляем model_info для совместимости с AssistantAgent
        self.model_info = {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "resilient_client"
        }
        
        logger.info(f"Initialized ResilientClient with tier '{model_tier}', fallback chain: {self.fallback_chain}")
    
    def _get_current_model(self) -> str:
        """Возвращает текущую модель из цепочки"""
        if self.current_model_index >= len(self.fallback_chain):
            # Если все модели исчерпаны, возвращаемся к первой
            self.current_model_index = 0
        return self.fallback_chain[self.current_model_index]
    
    def _switch_to_next_model(self) -> bool:
        """Переключается на следующую модель в цепочке. Возвращает True если есть куда переключаться"""
        self.current_model_index += 1
        if self.current_model_index >= len(self.fallback_chain):
            logger.warning(f"All models in chain exhausted for tier '{self.model_tier}'")
            return False
        
        new_model = self._get_current_model()
        logger.info(f"Switching to fallback model: {new_model}")
        return True
    
    async def create(self, *args, **kwargs):
        """
        Создает запрос с автоматическим fallback при ошибках
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            current_model = self._get_current_model()
            
            try:
                # Создаем клиент для текущей модели
                client = OpenAIChatCompletionClient(
                    model=current_model,
                    base_url=self.base_url,
                    api_key=self.api_key,
                    model_capabilities={
                        "vision": False,
                        "function_calling": True,
                        "json_output": True
                    }
                )
                
                logger.debug(f"Attempt {attempt + 1}/{self.max_retries} with model: {current_model}")
                
                # Выполняем запрос
                result = await client.create(*args, **kwargs)
                
                # Успех! Возвращаем результат
                if attempt > 0:
                    logger.info(f"✅ Success with fallback model: {current_model}")
                
                return result
                
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                # Определяем тип ошибки
                is_rate_limit = "429" in error_str or "rate_limit" in error_str.lower()
                is_server_error = "500" in error_str or "internal" in error_str.lower()
                is_auth_error = "auth" in error_str.lower() or "401" in error_str or "403" in error_str
                
                logger.warning(f"❌ Model {current_model} failed: {error_str[:100]}")
                
                # Если это ошибка авторизации или rate limit, пробуем следующую модель
                if is_auth_error or is_rate_limit or is_server_error:
                    if not self._switch_to_next_model():
                        # Все модели исчерпаны
                        logger.error(f"All fallback models failed for tier '{self.model_tier}'")
                        raise Exception(f"All models failed. Last error: {error_str}") from e
                    
                    # Пробуем следующую модель
                    continue
                else:
                    # Для других ошибок не переключаемся, просто повторяем
                    if attempt < self.max_retries - 1:
                        logger.info(f"Retrying with same model (attempt {attempt + 2}/{self.max_retries})...")
                        continue
                    else:
                        raise
        
        # Если дошли сюда, значит все попытки исчерпаны
        raise last_error

def create_resilient_client(role: str, base_url: str, api_key: str) -> ResilientClient:
    """
    Фабрика для создания resilient клиентов по роли
    """
    # Определяем tier по роли
    tier_map = {
        "architect": "premium",
        "reviewer": "premium",
        "manager": "standard",
        "coder_frontend": "fast",
        "coder_backend": "fast",
        "tester": "standard"
    }
    
    tier = tier_map.get(role, "standard")
    return ResilientClient(tier, base_url, api_key, max_retries=3)
