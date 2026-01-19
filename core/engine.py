import asyncio
from typing import List
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console

class SwarmEngine:
    def __init__(self):
        pass

    async def run_task_with_review(self, task: str, agents: List[Any]):
        """
        Запускает задачу в группе, где агенты должны договориться.
        Завершается, когда ревьюер пишет APPROVED или достигнут лимит сообщений.
        """
        # Условие завершения: либо слово APPROVED, либо 15 сообщений
        termination = TextMentionTermination("APPROVED") | MaxMessageTermination(15)
        
        team = RoundRobinGroupChat(
            agents=agents,
            termination_condition=termination
        )
        
        print(f"\n🚀 Starting Swarm Task: {task[:100]}...")
        async for message in team.run_stream(task=task):
            # Мы используем run_stream, чтобы видеть живой диалог
            if hasattr(message, 'content'):
                print(f"\n[{message.source}] > {message.content[:200]}...")
        
        return "Task completed or terminated."