import asyncio
from typing import List, Any
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

class SwarmEngine:
    async def run_task_with_review(self, task: str, agents: List[Any]):
        """
        Запускает задачу в Swarm-режиме.
        Агенты сами используют инструменты и общаются друг с другом.
        """
        # Завершаем, если ревьюер сказал APPROVED или прошло 20 сообщений
        termination = TextMentionTermination("APPROVED") | MaxMessageTermination(20)
        
        # Создаем команду
        team = RoundRobinGroupChat(
            agents=agents,
            termination_condition=termination
        )
        
        print(f"\n[SYSTEM] >>> Starting task: {task[:100]}...")

        # Запускаем поток сообщений
        async for message in team.run_stream(task=task):
            # Логируем в консоль, кто что сказал/сделал
            source = getattr(message, 'source', 'Assistant')
            content = getattr(message, 'content', '')
            
            if content:
                print(f"\n[{source}] > {content[:500]}")
            
            # Если агент вызвал инструмент, мы это тоже увидим
            if hasattr(message, 'models_usage') and message.models_usage:
                print(f"   (Tokens used: {message.models_usage})")
        
        print("\n[SYSTEM] >>> Task sequence finished.")
        return "DONE"