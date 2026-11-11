import asyncio
import os

from agent_framework import Agent, ChatResponse
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

question = "Show me the mathemical equation for Starlink satellites distance from earth calculation" #"Tell me a joke about programmers"  # Then ask something more complicated like "Show me the mathemical equation for Starlink satellites distance from earth calculation"

# Notice the difference between the 2 models chosen by the model-router for different types of questions

agent = Agent(client=OpenAIChatCompletionClient(model="model-router", async_client=openai_client))

MAGENTA = "\033[95m"
RESET = "\033[0m"


async def main() -> None:
    response = await agent.run(question)
    print(response)

    usage = response.usage_details
    if usage:
        raw = response.raw_representation
        model_used = raw.model if isinstance(raw, ChatResponse) else None
        print(MAGENTA)
        print(f"The model used for this response: {model_used}")
        print(f"Input Tokens: {usage.get('input_token_count')}")
        print(f"Cached Tokens: {usage.get('cache_read_input_token_count') or 0}")
        print(f"Output Tokens: {usage.get('output_token_count')}")
        print(f"Reasoning Tokens: {usage.get('reasoning_output_token_count') or 0}")
        print(f"Total Tokens: {usage.get('total_token_count')}", end="")
        print(RESET)


if __name__ == "__main__":
    asyncio.run(main())
