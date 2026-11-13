from datetime import datetime
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
            name="Chart Agent",
            instructions="You can make charts using your Code Interpreter tool",
            tools=client.get_code_interpreter_tool(),
        )

    response = await agent.run("Create a pie chart showing the 5 most populous countries in the world")
    print(response)

    raw_openai = client.client 
    seen: set[tuple[str, str]] = set()
 
    for message in response.messages:
        for content in message.contents:
            for annotation in content.annotations or []:
                file_id = annotation.get("file_id")
                container_id = (annotation.get("additional_properties") or {}).get("container_id")
                if not file_id or not container_id:
                    continue
 
                key = (container_id, file_id)
                if key in seen:  # the same file is cited once per text span
                    continue
                seen.add(key)
 
                # annotation["url"] carries the filename for container_file_citation
                filename = annotation.get("url") or file_id
 
                file_content = await raw_openai.containers.files.content.retrieve(
                    file_id, container_id=container_id
                )
                media_dir = Path(__file__).parent / "media"
                media_dir.mkdir(parents=True, exist_ok=True)
                path = media_dir / Path(filename).name
                path.write_bytes(file_content.content)
 
                print(f"Attempting to open: '{path}'")
                print(f"File exists: {path.exists()}")
                os.startfile(path)

    usage = response.usage_details
    if usage:
        print("\n--- Token Usage ---")
        print(f"Input Tokens: {usage.get('input_token_count', 'N/A')}")
        print(f"Output Tokens: {usage.get('output_token_count', 'N/A')}")
        print(f"Reasoning Tokens: {usage.get('openai.reasoning_tokens', 'N/A')}")
        print(f"Total Tokens: {usage.get('total_token_count', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main())