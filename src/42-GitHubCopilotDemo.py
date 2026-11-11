import asyncio
import os
import time

from agent_framework import tool
from agent_framework.github import GitHubCopilotAgent, GitHubCopilotOptions
from copilot import CopilotClient
from copilot.session import PermissionHandler
from dotenv import load_dotenv

load_dotenv()

MAGENTA = "\033[95m"
GREEN = "\033[92m"
RESET = "\033[0m"


@tool(name="get_weather", approval_mode="never_require")
def get_weather(location: str) -> str:
    # Replace this with your actual weather fetching logic
    return f"The weather in {location} is sunny."


async def main() -> None:
    client = CopilotClient(
        # use_logged_in_user=False,
        # github_token=os.getenv("GITHUB_TOKEN"),
    )

    try:
        agent = GitHubCopilotAgent(
            client=client,
            tools=[get_weather],
            default_options=GitHubCopilotOptions(
                model="gpt-6-luna",
                working_directory=os.getcwd(),
                on_permission_request=PermissionHandler.approve_all,
            ),
        )

        async with agent:
            start = time.perf_counter()

            response = await agent.run("What is the weather in Orlando?")

            milliseconds = int((time.perf_counter() - start) * 1000)

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

            print(f"{GREEN}Time spent: {milliseconds} ms{RESET}")
    finally:
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
