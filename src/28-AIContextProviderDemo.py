import asyncio
import os
from typing import Any

from agent_framework import Agent, AgentSession, ContextProvider, SessionContext, SupportsAgentRun
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Equivalent of the .NET user secrets: reads "endpoint" and "apikey" from env vars or a .env file
load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
apikey = os.getenv("AZURE_OPENAI_API_KEY")

openai_client = AsyncOpenAI(
    api_key=apikey,
    base_url=endpoint + "/openai/v1/",
)

MAGENTA = "\033[95m"
RESET = "\033[0m"

# If you don't want to use the APIKey, you can use Bearer token authentication instead
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
# openai_client = AsyncOpenAI(
#     api_key=token_provider,
#     base_url=endpoint + "/openai/v1/",
# )


class MyAIContextProvider(ContextProvider):
    """
    Order of a ContextProvider when an 'agent.run' method is being executed

    - before_run
    - LLM Call
    - after_run

    """

    def __init__(self) -> None:
        super().__init__(source_id="my_ai_context_provider")

    # Pre LLM Call (Enrichment)
    async def before_run(
        self,
        *,
        agent: SupportsAgentRun,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """
        Use this to do the following:
        - Inject additional instructions (for this one LLM Call)
        - Inject additional tools (for this one LLM Call)
        - Inject additional message (that unlike the two above will become part of chat-history)
        """
        print(MAGENTA)
        print("Before LLM call: extending instructions and tools")
        print(RESET)
        context.extend_instructions(self.source_id, "Speak like Mickey Mouse")
        context.extend_tools(self.source_id, [])

    # Post LLM Call (Leverage LLM Call Result for something)
    async def after_run(
        self,
        *,
        agent: SupportsAgentRun,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """
        Use this to do the following:
        - Extract information out of the response in a centralized structured manner (aka example storing memory)
        - Deal with exceptions
        """
        print(MAGENTA)
        print("After LLM call: processing response")
        print(RESET)


question = "What are the top 10 Movies according to IMDB?"

agent = Agent(
    client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
    instructions="Prefix all messages with Hi Lino, and suffix all messages with Cheers, Lino.",
    context_providers=[MyAIContextProvider()],
)


async def main() -> None:
    response = await agent.run(question)
    print(response)

    usage = response.usage_details
    if usage:
        print(MAGENTA)
        print(f"Input Tokens: {usage.get('input_token_count')}")
        print(f"Cached Tokens: {usage.get('cache_read_input_token_count') or 0}")
        print(f"Output Tokens: {usage.get('output_token_count')}")
        print(f"Reasoning Tokens: {usage.get('reasoning_output_token_count') or 0}")
        print(f"Total Tokens: {usage.get('total_token_count')}", end="")
        print(RESET)


if __name__ == "__main__":
    asyncio.run(main())
