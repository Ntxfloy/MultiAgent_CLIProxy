import asyncio
import os
from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents.registry_v2 import AgentRegistry
from core.engine import SwarmEngine
from tools.file_ops import write_file, read_file, list_files

async def main():
    # 1. Настройка API
    api_key = os.getenv("OPENAI_API_KEY", "test-key")
    
    # Сильная модель для Ревьюера (Senior)
    smart_model = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)
    
    # Быстрая и дешевая модель для Кодера (Junior/Mid)
    fast_model = OpenAIChatCompletionClient(model="gpt-4o-mini", api_key=api_key)

    # 2. Инструменты
    tools = [write_file, read_file, list_files]

    # 3. Создание агентов
    registry = AgentRegistry()
    coder = registry.create_coder("junior_coder", "Frontend", fast_model, tools)
    reviewer = registry.create_reviewer("senior_reviewer", smart_model, tools)

    # 4. Движок
    engine = SwarmEngine()

    # 5. Задача
    task = """Task: Create a simple 'AI NEXUS' home page in HTML/CSS.
    1. Use write_file to save it as 'index.html'.
    2. Use cyberpunk styles (dark background, neon colors).
    3. Reviewer must check the file content after creation.
    """

    await engine.run_task_with_review(task, [coder, reviewer])

if __name__ == "__main__":
    asyncio.run(main())