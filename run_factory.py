import asyncio
import os
import sys
from datetime import datetime
from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents.registry_v3 import AgentRegistry
from core.swarm import SwarmTeam
from tools.file_ops import write_file, read_file, list_files
from config import MODELS, BASE_URL, API_KEY
from core.resilient_client import create_resilient_client

# Создаем лог-файл с timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/session_{timestamp}.log"
os.makedirs("logs", exist_ok=True)

class DualLogger:
    """Пишет и в консоль, и в файл"""
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()

async def main():
    # Перенаправляем вывод в файл + консоль
    sys.stdout = DualLogger(log_file)
    
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Create a Cyberpunk AI Chat app."
    api_key = os.getenv("OPENAI_API_KEY", "test-key-123")

    # Клиент с автоматическим fallback
    def make_client(role):
        return create_resilient_client(role, BASE_URL, api_key)

    tools = [write_file, read_file, list_files]
    registry = AgentRegistry()
    
    manager = registry.create_manager(make_client("manager"), tools)
    architect = registry.create_architect(make_client("architect"), tools)
    coder_fe = registry.create_coder("frontend_dev", "React/TS", make_client("coder_frontend"), tools)
    coder_be = registry.create_coder("backend_dev", "Python/FastAPI", make_client("coder_backend"), tools)
    reviewer = registry.create_reviewer(make_client("reviewer"), tools)

    swarm = SwarmTeam(selector_model=make_client("reviewer"))

    print(f"\n{'='*60}")
    print(f"🚀 FACTORY SESSION: {timestamp}")
    print(f"📝 Log file: {log_file}")
    print(f"🎯 Task: {user_prompt}")
    print(f"{'='*60}\n")
    
    try:
        await swarm.execute_task(
            f"Build {user_prompt}. Work until Reviewer says APPROVED. Architect: plan. Coders: implement. Reviewer: verify and approve when done.",
            [manager, architect, coder_fe, coder_be, reviewer],
            max_steps=200  # Увеличил лимит
        )
        print(f"\n✅ Session completed! Log saved to: {log_file}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"📋 Partial log saved to: {log_file}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
