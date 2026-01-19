$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# 1. Фикс swarm.py
$swarmContent = @'
import asyncio
from typing import List, Any
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

class SwarmTeam:
    def __init__(self, selector_model: Any):
        self.selector_model = selector_model

    async def execute_task(self, task: str, agents: List[Any], max_steps: int = 30):
        termination = TextMentionTermination("APPROVED") | MaxMessageTermination(max_steps)
        
        # В AutoGen 0.4.x используется participants вместо agents
        team = SelectorGroupChat(
            participants=agents,
            model_client=self.selector_model, # Модель, которая выбирает следующего спикера
            termination_condition=termination
        )

        print(f"\n[SWARM] Executing task: {task[:100]}...")

        async for message in team.run_stream(task=task):
            source = getattr(message, 'source', 'AI')
            content = getattr(message, 'content', '')
            if content:
                print(f"\n>>> {source}:\n{content[:800]}\n")
        return "Task complete."
'@

# 2. Фикс run_factory.py
$factoryContent = @'
import asyncio
import os
import sys
from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents.registry_v3 import AgentRegistry
from core.swarm import SwarmTeam
from tools.file_ops import write_file, read_file, list_files
from config import MODELS, BASE_URL, API_KEY

async def main():
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Create a Cyberpunk AI Chat app."
    api_key = os.getenv("OPENAI_API_KEY", "test-key-123")

    def make_client(role):
        return OpenAIChatCompletionClient(
            model=MODELS[role], base_url=BASE_URL, api_key=api_key,
            model_capabilities={"vision": False, "function_calling": True, "json_output": True}
        )

    tools = [write_file, read_file, list_files]
    registry = AgentRegistry()
    
    # Инициализируем агентов
    manager = registry.create_manager(make_client("manager"), tools)
    architect = registry.create_architect(make_client("architect"), tools)
    coder_fe = registry.create_coder("frontend_dev", "React/TS", make_client("coder_frontend"), tools)
    coder_be = registry.create_coder("backend_dev", "Python/FastAPI", make_client("coder_backend"), tools)
    reviewer = registry.create_reviewer(make_client("reviewer"), tools)

    # Движок Swarm теперь требует модель-селектор (используем Sonnet)
    swarm = SwarmTeam(selector_model=make_client("reviewer"))

    print(f"\n--- STARTING FACTORY: {user_prompt} ---")
    await swarm.execute_task(
        f"Build {user_prompt}. Architect: plan first. Coders: implement. Reviewer: verify.",
        [manager, architect, coder_fe, coder_be, reviewer]
    )

if __name__ == "__main__":
    asyncio.run(main())
'@

Set-Content -Path (Join-Path $ScriptDir "core\swarm.py") -Value $swarmContent -Encoding UTF8
Set-Content -Path (Join-Path $ScriptDir "run_factory.py") -Value $factoryContent -Encoding UTF8
Write-Host "✅ Fixed API (agents -> participants) and Selector logic." -ForegroundColor Green