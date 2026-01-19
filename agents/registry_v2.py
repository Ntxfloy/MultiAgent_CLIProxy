from typing import List, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class AgentRegistry:
    def create_coder(self, name: str, area: str, model_client: OpenAIChatCompletionClient, tools: List[Any]) -> AssistantAgent:
        return AssistantAgent(
            name=name,
            model_client=model_client,
            tools=tools,
            system_message=f"""You are a Senior {area} Coder.
Your goal: Implement high-quality code.
Rules:
1. Use 'write_file' to save code.
2. Use 'read_file' to check logic.
3. If Reviewer says there is an error, FIX IT immediately.
4. You are DONE only when Reviewer writes 'APPROVED'."""
        )

    def create_reviewer(self, name: str, model_client: OpenAIChatCompletionClient, tools: List[Any]) -> AssistantAgent:
        return AssistantAgent(
            name=name,
            model_client=model_client,
            tools=tools,
            system_message="""You are a QA & Code Reviewer.
Your goal: Ensure code is perfect.
Rules:
1. Use 'read_file' to check Coder's work.
2. If find bugs, tell Coder to fix them.
3. Write 'APPROVED' only if code is perfect and task is finished."""
        )