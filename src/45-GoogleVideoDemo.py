import asyncio
import base64
import os
import textwrap

import httpx
from dotenv import load_dotenv

load_dotenv()
apikey = os.getenv("GOOGLE_API_KEY")

request = {
    "model": "gemini-omni-1.2-flash",
    "input": textwrap.dedent("""\
        Create a short promotional video for a software conference. 
        A fictional adult presenter with an enthusiastic, professional manner stands outside a modern convention 
        center in Orlando, Florida, on a sunny day. The presenter holds a plain microphone and speaks directly to 
        the camera: Join us in Orlando, November sixteenth through nineteenth, twenty twenty-six, for exciting sessions 
        and hands-on workshops about Microsoft Agent Framework!
        Use a steady medium shot, natural lighting, clear speech, and subtle outdoor ambience. This is a staged conference 
        promotion featuring an original fictional character. Use neutral clothing and an unbranded building, without broadcaster 
        logos or news graphics.
        
        """).rstrip("\n"),
    "response_format": {
        "type": "video",
        "duration": "10s",
        "aspect_ratio": "16:9",
        "resolution": "720p",
    },
}


async def main() -> None:
    async with httpx.AsyncClient(timeout=httpx.Timeout(600), headers={"x-goog-api-key": apikey}) as client:
        response = await client.post("https://generativelanguage.googleapis.com/v1beta/interactions", json=request)

    if not response.is_success:
        raise httpx.HTTPStatusError(
            f"Google API returned {response.status_code}: {response.text}", request=response.request, response=response
        )

    document = response.json()
    saved = 0

    for step in document["steps"]:
        if step.get("type") != "model_output" or "content" not in step:
            continue

        for content in step["content"]:
            content_type = content.get("type")
            if content_type is None:
                continue

            if content_type == "text" and "text" in content:
                print(content["text"])
            elif content_type == "video" and "data" in content:
                mime_type = content.get("mime_type")
                if mime_type is None:
                    raise RuntimeError("Video MIME type is missing.")

                if mime_type != "video/mp4":
                    raise RuntimeError(f"Unexpected video type: {mime_type}")

                if content["data"] is None:
                    raise RuntimeError("Video data is missing.")
                video_bytes = base64.b64decode(content["data"])

                saved += 1
                media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
                os.makedirs(media_dir, exist_ok=True)
                path = os.path.join(media_dir, f"generatedVideo-{saved}.mp4")

                with open(path, "wb") as f:
                    f.write(video_bytes)
                print(f"Saved: {path}")

    if saved == 0:
        raise RuntimeError("The response contained no video.")


if __name__ == "__main__":
    asyncio.run(main())
