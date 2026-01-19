import asyncio
import os
from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents.registry_v2 import AgentRegistry
from core.engine_v2 import SwarmEngine
from tools.file_ops import write_file, read_file, list_files

async def main():
    # 1. API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        return

    # 2. Настройка асимметричных моделей
    # Ревьюер: Самый умный
    smart_model = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)
    # Кодер: Быстрый и дешевый
    fast_model = OpenAIChatCompletionClient(model="gpt-4o-mini", api_key=api_key)

    # 3. Реестр и инструменты
    registry = AgentRegistry()
    tools = [write_file, read_file, list_files]

    # 4. Создание команды
    junior_coder = registry.create_coder("junior_coder", "Frontend", fast_model, tools)
    senior_reviewer = registry.create_reviewer("senior_reviewer", smart_model, tools)

    # 5. Движок и задача
    engine = SwarmEngine()
    
    task = """TASK:
    1. Create a beautiful cyberpunk-styled 'index.html' in the workspace.
    2. Use dark theme with neon pink and cyan accents.
    3. After writing the file, senior_reviewer MUST read it and approve or request changes.
    """

    print("\n--- Swarm Session Start ---")
    await engine.run_task_with_review(task, [junior_coder, senior_reviewer])
    print("--- Swarm Session End ---")

if __name__ == "__main__":
    asyncio.run(main())