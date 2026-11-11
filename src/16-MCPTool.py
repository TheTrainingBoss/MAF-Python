from dotenv import load_dotenv
from agent_framework.openai import OpenAIChatClient
from agent_framework import Agent, MCPStreamableHTTPTool
import asyncio
import os

async def main():
    load_dotenv()

    client = OpenAIChatClient(
        api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        model=os.getenv('AZURE_OPENAI_MODEL'),
        azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    )

    async with MCPStreamableHTTPTool(
        name="Microsoft Learning Tool",
        url="https://learn.microsoft.com/api/mcp",
    ) as learn_tool:
        agent = Agent(
            client=client,
            instructions="You are a helpful assistant that provides accurate and concise information about Microsoft Agent Framework",
            name="Microsoft Learning Tool",
            description="Agent to respond with accurate Learning resources",
            tools=[learn_tool],
        )
        response = await agent.run("Create a simple sample in C# on how to create an agent in Agent Framework")

    print(response)

    usage = response.usage_details
    if usage:
        print("\n--- Token Usage ---")
        print(f"Input Tokens: {usage.get('input_token_count', 'N/A')}")
        print(f"Output Tokens: {usage.get('output_token_count', 'N/A')}")
        print(f"Reasoning Tokens: {usage.get('openai.reasoning_tokens', 'N/A')}")
        print(f"Total Tokens: {usage.get('total_token_count', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main())