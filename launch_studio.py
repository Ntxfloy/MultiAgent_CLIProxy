import asyncio
import os
from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents.registry_v3 import AgentRegistry
from core.swarm import SwarmTeam
from tools.file_ops import write_file, read_file, list_files
from config import MODELS, BASE_URL, API_KEY

async def main():
    # 1. Инициализация клиентов (через cliProxy)
    def make_client(role):
        return OpenAIChatCompletionClient(
            model=MODELS[role],
            base_url=BASE_URL,
            api_key=API_KEY,
            model_capabilities={"vision": False, "function_calling": True, "json_output": True}
        )

    # 2. Создание инструментов
    tools = [write_file, read_file, list_files]

    # 3. Регистрация агентов
    registry = AgentRegistry()
    
    manager = registry.create_manager(make_client("manager"), tools)
    architect = registry.create_architect(make_client("architect"), tools)
    coder_fe = registry.create_coder("frontend_dev", "Frontend", make_client("coder_frontend"), tools)
    coder_be = registry.create_coder("backend_dev", "Backend", make_client("coder_backend"), tools)
    reviewer = registry.create_reviewer(make_client("reviewer"), tools)

    swarm = SwarmTeam()

    # --- ПОЛНЫЙ ЦИКЛ РАЗРАБОТКИ ---

    # ЭТАП 1: Архитектура
    print("\n--- PHASE 1: ARCHITECTURE DESIGN ---")
    await swarm.execute_task(
        "Architect and Manager: Design the folder structure and interfaces for 'AI NEXUS STUDIO'. Write it to docs/plan.md",
        [manager, architect]
    )

    # ЭТАП 2: Реализация
    print("\n--- PHASE 2: PARALLEL IMPLEMENTATION ---")
    await swarm.execute_task(
        "Frontend, Backend and Reviewer: Implement the core functionality. FE: index.html + styles. CSS, BE: api.py. Reviewer: read and approve each file.",
        [coder_fe, coder_be, reviewer]
    )

    # ЭТАП 3: Финализация
    print("\n--- PHASE 3: FINAL REVIEW ---")
    await swarm.execute_task(
        "Manager and Reviewer: Check all files in workspace. If everything is correct and matches the plan, provide a final summary.",
        [manager, reviewer]
    )

if __name__ == "__main__":
    asyncio.run(main())