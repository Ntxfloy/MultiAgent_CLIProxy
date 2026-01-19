from typing import List, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class AgentRegistry:
    def create_manager(self, model_client: OpenAIChatCompletionClient, tools: List[Any]) -> AssistantAgent:
        return AssistantAgent(
            name="project_manager",
            model_client=model_client,
            tools=tools,
            system_message="""You are a Project Manager.
Your goal: Orchestrate the development process.
1. Look at the workspace and tasks.
2. Ensure the Architect has created a plan first.
3. Coordinate Coders and Reviewers.
4. You are responsible for the final project delivery."""
        )

    def create_architect(self, model_client: OpenAIChatCompletionClient, tools: List[Any]) -> AssistantAgent:
        return AssistantAgent(
            name="architect",
            model_client=model_client,
            tools=tools,
            system_message="""You are a Lead Architect.
Your goal: Design the system architecture.
1. Create 'docs/architecture.md' and 'docs/interfaces.md'.
2. Define file structure and technology stack.
3. Make sure Coders follow your design."""
        )

    def create_coder(self, name: str, role: str, model_client: OpenAIChatCompletionClient, tools: List[Any]) -> AssistantAgent:
        return AssistantAgent(
            name=name,
            model_client=model_client,
            tools=tools,
            system_message=f"""You are a Senior {role} Developer.
Your goal: Implement the features according to the architecture.
1. Read docs/architecture.md before coding.
2. Use write_file to implement logic.
3. Wait for Reviewer approval."""
        )

    def create_reviewer(self, model_client: OpenAIChatCompletionClient, tools: List[Any]) -> AssistantAgent:
        return AssistantAgent(
            name="senior_reviewer",
            model_client=model_client,
            tools=tools,
            system_message="""You are a Senior QA/Code Reviewer.
Your goal: Zero-bug policy.
1. Read files and check for logic errors, security holes, and style.
2. Request fixes if needed.
3. Write 'APPROVED' only when the code is perfect."""
        )