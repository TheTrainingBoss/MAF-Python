import asyncio
import base64
import os
from collections.abc import Iterator
from typing import Any

from agent_framework import Agent
from agent_framework.gemini import GeminiChatClient
from dotenv import load_dotenv
from google.genai import types

# Equivalent of the .NET user secret "Google:ApiKey": reads GOOGLE_API_KEY from env vars or a .env file
load_dotenv()
apikey = os.getenv("GOOGLE_API_KEY")

# For Nano Banana 2, use "gemini-3.1-flash-image".
# For Nano Banana Pro use "gemini-3-pro-image"
MODEL_ID = "gemini-3.1-flash-image"

chat_client = GeminiChatClient(api_key=apikey, model=MODEL_ID)

# Options that aren't declared on GeminiChatOptions are passed through as-is to Gemini's GenerateContentConfig
chat_options: dict[str, Any] = {
    "response_modalities": ["TEXT", "IMAGE"],
    "image_config": types.ImageConfig(aspect_ratio="1:1", image_size="2K"),
}

agent = Agent(
    client=chat_client,
    name="ImageGenerator",
    default_options=chat_options,
)

EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}

MAGENTA = "\033[95m"
RESET = "\033[0m"


def gemini_images(raw: Any, depth: int = 0) -> Iterator[tuple[str, bytes]]:
    """Find image parts in the raw Gemini response (walks the raw_representation chain)."""
    if raw is None or depth > 5:
        return
    if isinstance(raw, list):
        for item in raw:
            yield from gemini_images(item, depth + 1)
    elif isinstance(raw, types.GenerateContentResponse):
        for candidate in raw.candidates or []:
            for part in (candidate.content.parts if candidate.content else None) or []:
                blob = part.inline_data
                if blob and blob.data and (blob.mime_type or "").lower().startswith("image/"):
                    yield blob.mime_type.lower(), blob.data
    else:
        yield from gemini_images(getattr(raw, "raw_representation", None), depth + 1)


async def main() -> None:
    saved = 0

    imageresponse = await agent.run("Create an image of a cute Havaneese dog")

    images: list[tuple[str, bytes]] = []
    for content in (c for m in imageresponse.messages for c in m.contents):
        if content.type == "text":
            print(content.text)
        elif content.type == "data" and (content.media_type or "").lower().startswith("image/") and content.uri:
            images.append((content.media_type.lower(), base64.b64decode(content.uri.split(",", 1)[1])))

    # The Python Gemini client currently only converts text parts, so images are read from the raw Gemini response
    if not images:
        images = list(gemini_images(imageresponse.raw_representation))

    media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
    os.makedirs(media_dir, exist_ok=True)

    for media_type, data in images:
        extension = EXTENSIONS.get(media_type, ".bin")
        saved += 1
        path = os.path.join(media_dir, f"generated-{saved}{extension}")
        with open(path, "wb") as f:
            f.write(data)
        print(f"Saved: {path}")

    if saved == 0:
        print("The model returned no image. Review its text response.")

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
