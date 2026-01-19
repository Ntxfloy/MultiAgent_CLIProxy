import asyncio
from typing import List, Any
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination

class SwarmTeam:
    def __init__(self, selector_model: Any):
        self.selector_model = selector_model

    async def execute_task(self, task: str, agents: List[Any], max_steps: int = 200):
        # Используем только MaxMessageTermination, проверку APPROVED делаем вручную
        termination = MaxMessageTermination(max_steps)
        
        team = SelectorGroupChat(
            participants=agents,
            model_client=self.selector_model,
            termination_condition=termination
        )

        print(f"\n[SWARM] Starting task (max {max_steps} steps)...")
        print(f"[SWARM] Task: {task[:150]}...\n")

        try:
            message_count = 0
            async for message in team.run_stream(task=task):
                message_count += 1
                source = getattr(message, 'source', 'AI')
                content = getattr(message, 'content', '')
                
                if content and source != 'user':  # Не показываем повтор промпта пользователя
                    # Обрезаем длинные сообщения для читаемости
                    display_content = content[:1000] + "..." if len(content) > 1000 else content
                    print(f"\n>>> {source}:")
                    print(f"{display_content}\n")
                    print("-" * 80)
                
                # Проверяем на APPROVED только от reviewer
                if source == "senior_reviewer" and "APPROVED" in content.upper():
                    print(f"\n🎉 APPROVED by {source}! Task complete.")
                    break
                    
        except Exception as e:
            print(f"\n⚠️ Swarm error: {e}")
            import traceback
            traceback.print_exc()
            
        print(f"\n[SWARM] Total messages: {message_count}")
        return "Task execution finished."
