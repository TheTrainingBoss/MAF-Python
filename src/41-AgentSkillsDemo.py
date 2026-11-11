import asyncio
import os

from agent_framework import Agent, Message, SkillsProvider
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
apikey = os.getenv("AZURE_OPENAI_API_KEY")

openai_client = AsyncOpenAI(
    api_key=apikey,
    base_url=endpoint + "/openai/v1/",
)

# If you don't want to use the APIKey, you can use Bearer token authentication instead
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
# openai_client = AsyncOpenAI(
#     api_key=token_provider,
#     base_url=endpoint + "/openai/v1/",
# )


async def main() -> None:
    path = os.path.join(os.getcwd(), "AgentSkills")
    print(f"Loading skills from: {path}")
    skills_provider = SkillsProvider.from_paths(skill_paths=path)

    agent = Agent(
        client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
        name="Mickey Mouse",
        instructions="You are a helpful assistant. Answer questions and complete tasks for the user to the best of your ability. If you don't know the answer to a question, say you don't know.",
        context_providers=[skills_provider],
    )

    session = agent.create_session()
    response = await agent.run("Why is the sky blue? use one of the skills available to you to answer as if your are talking to a 5 year old", session=session)

    # The SkillsProvider exposes skill-loading as a tool call that requires approval.
    # Without approving it (on the same session), run stops after the approval request and returns no text.
    # (Alternatively: middleware=[ToolApprovalMiddleware(auto_approval_rules=[SkillsProvider.all_tools_auto_approval_rule])])
    while approval_requests := [c for c in response.user_input_requests if c.type == "function_approval_request"]:
        approvals = [request.to_function_approval_response(approved=True) for request in approval_requests]

        response = await agent.run(Message(role="user", contents=approvals), session=session)

    print(f"Agent: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
