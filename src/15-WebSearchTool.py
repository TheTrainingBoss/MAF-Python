from datetime import datetime
from click import open_file
from dotenv import load_dotenv
from agent_framework.openai import OpenAIChatClient
from agent_framework import Agent, tool
from agent_framework._types import AgentResponse
import asyncio
import os
from pathlib import Path

async def main():
    load_dotenv()

    client = OpenAIChatClient(
        api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        model=os.getenv('AZURE_OPENAI_MODEL'),
        azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    )

    agent = client.as_agent(
            name="Football Search Agent",
            instructions="You can use the web search tool to find information online",
            tools=[client.get_web_search_tool(), get_date_time],
        )

    response = await agent.run("What is the score between the 49ers and the Raiders football game played in Santa Clara in November 2026?")
    print(response)

    usage = response.usage_details
    if usage:
        print("\n--- Token Usage ---")
        print(f"Input Tokens: {usage.get('input_token_count', 'N/A')}")
        print(f"Output Tokens: {usage.get('output_token_count', 'N/A')}")
        print(f"Reasoning Tokens: {usage.get('openai.reasoning_tokens', 'N/A')}")
        print(f"Total Tokens: {usage.get('total_token_count', 'N/A')}")

@tool(approval_mode="never_require")
def get_date_time() -> str:
    """Get the current date and time."""
    print("Getting current date and time from the tool...")
    return f"The current date and time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."

if __name__ == "__main__":
    asyncio.run(main())