from dotenv import load_dotenv
from agent_framework.openai import OpenAIChatClient
from agent_framework import Agent, FunctionInvocationContext, function_middleware, tool
import asyncio
import os
from typing import Any
from datetime import datetime, timezone

async def main():
    load_dotenv()

    client = OpenAIChatClient(
        api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        model=os.getenv('AZURE_OPENAI_MODEL'),
        azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    )

    football_agent = Agent(
        client=client,
        instructions=(
            "You are an expert in Football statistics. Use the date and time tool "
            "whenever current date/time context is required. Use the web search tool "
            "for any information that is not available in your training data. Always "
            "provide sources for your information."
        ),
        name="Football Bot",
        description="Football Bot that provides current football statistics",
        tools=[get_current_datetime, client.get_web_search_tool()],
    )

    agent = Agent(
        client=client,
        instructions="You are a helpful assistant. Refer all requests about football statistics to the Football Bot.",
        name="Main Agent",
        description="An assistant that provides weather information and football statistics.",
        tools=[football_agent.as_tool()],
        middleware=[middleware],
    )

    response = await agent.run("How many games per season are played in the premier league by all teams?")
    print(response)

    usage = response.usage_details
    if usage:
        print("\n--- Token Usage ---")
        print(f"Input Tokens: {usage.get('input_token_count', 'N/A')}")
        print(f"Output Tokens: {usage.get('output_token_count', 'N/A')}")
        print(f"Reasoning Tokens: {usage.get('openai.reasoning_tokens', 'N/A')}")
        print(f"Total Tokens: {usage.get('total_token_count', 'N/A')}")

@function_middleware
async def middleware(
    context: FunctionInvocationContext,
    call_next: Any,
) -> Any:
    """Function middleware to intercept and log tool calls and arguments."""
    tool_details = f"- Tool Call: '{context.function.name}'"
    items: list[tuple[str, Any]] = []

    if context.arguments:
        if isinstance(context.arguments, dict):
            items = list(context.arguments.items())
        elif hasattr(context.arguments, "model_dump"):
            items = list(context.arguments.model_dump().items())

    if items:
        args_str = ", ".join(f"[{k} = {v}]" for k, v in items)
        tool_details += f" (Args: {args_str})"

    print(tool_details)
    return await call_next()

@tool(name="get_current_datetime", description="Get the current date and time in UTC.")
def get_current_datetime() -> str:
    """Gets the current date and time in UTC format."""
    return datetime.now(timezone.utc).isoformat()

if __name__ == "__main__":
    asyncio.run(main())