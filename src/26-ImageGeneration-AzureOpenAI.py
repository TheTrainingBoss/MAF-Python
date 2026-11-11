import asyncio
import base64
import os
import tempfile
import uuid
from urllib.parse import urljoin

from agent_framework import Agent, Content
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
apikey = os.getenv("AZURE_OPENAI_API_KEY")

# Azure OpenAI needs this header to know which image generation deployment the hosted tool should use
openai_client = AsyncOpenAI(
    api_key=apikey,
    base_url=urljoin(endpoint, "/openai/v1/"),
    default_headers={"x-ms-oai-image-generation-deployment": "gpt-image-2.5-flare"},
)

client = OpenAIChatClient(model="gpt-5", async_client=openai_client)

agent = Agent(
    client=client,
    tools=[
        client.get_image_generation_tool(
            output_format="png",
            model="gpt-image-2.5-flare",
        )
    ],
)

MAGENTA = "\033[95m"
RESET = "\033[0m"


def save_and_open_image(data_content: Content) -> None:
    if not data_content.uri or ";base64," not in data_content.uri:
        return
    media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
    os.makedirs(media_dir, exist_ok=True)
    path = os.path.join(media_dir, f"image-{uuid.uuid4().hex}.png")
    with open(path, "wb") as f:
        f.write(base64.b64decode(data_content.uri.split(";base64,", 1)[1]))
    print(f"Image saved to: {path}")
    # Equivalent of Process.Start with UseShellExecute = true (opens with the default image viewer)
    os.startfile(path)



async def main() -> None:
    imageresponse = await agent.run("Create an image of a cute Havaneese dog")

    for message in imageresponse.messages:
        for content in message.contents:
            if content.type == "image_generation_tool_result":
                outputs = content.outputs or []
                if isinstance(outputs, Content):
                    outputs = [outputs]
                for ai_content in outputs:
                    if isinstance(ai_content, Content) and ai_content.type == "data":
                        save_and_open_image(ai_content)

    usage = imageresponse.usage_details
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
