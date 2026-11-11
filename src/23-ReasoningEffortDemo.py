import asyncio
import os

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
apikey = os.getenv('AZURE_OPENAI_API_KEY')

QUESTION = "Who is Bill Gates? and where was he born?"


openai_client = AsyncOpenAI(
    api_key=apikey,
    base_url=endpoint + "/openai/v1/",
    timeout=60,
)

# If you don't want to use the APIKey, you can use Bearer token authentication instead
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
# openai_client = AsyncOpenAI(
#     api_key=token_provider,
#     base_url=endpoint + "/openai/v1/",
#     timeout=60,
# )


def create_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client)


def print_usage(response, reasoning_effort: str) -> None:
    usage = response.usage_details or {}
    print("Reasoning Effort: " + reasoning_effort)
    print("Input Token Count: " + str(usage.get("input_token_count")))
    print("Output Token Count: " + str(usage.get("output_token_count")))
    print("Reasoning Token Count: " + str(usage.get("reasoning_output_token_count")))


async def main() -> None:
    # This is set to the default of Medium for reasonning efforts
    agent = Agent(client=create_client())

    response = await agent.run(QUESTION)
    print(response)
    print_usage(response, "medium (default)")

    # Let's take control of the reasonning efforts
    reasoning_effort = "high"
    agent_with_reasoning_effort = Agent(
        client=create_client(),
        default_options={"reasoning_effort": reasoning_effort},
    )

    response_with_reasoning_effort = await agent_with_reasoning_effort.run(QUESTION)
    print(response_with_reasoning_effort)
    print_usage(response_with_reasoning_effort, reasoning_effort)


if __name__ == "__main__":
    asyncio.run(main())
