import asyncio
import base64
import os

from agent_framework import Agent, Content, Message
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()
openaiapikey = os.getenv("OPENAI_API_KEY")

# For PDF we have to use OpenAI, still not supported in Azure OpenAI
client = OpenAIChatCompletionClient(model="gpt-5", api_key=openaiapikey)

# This is set to the default of Medium for reasonning efforts
agent = Agent(client=client)

MAGENTA = "\033[95m"
RESET = "\033[0m"


async def main() -> None:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media", "englishdriverhandbook.pdf")
    with open(path, "rb") as f:
        base64pdf = base64.b64encode(f.read()).decode("ascii")
    data_uri = f"data:application/pdf;base64,{base64pdf}"

    pdfresponse = await agent.run(
        Message(
            role="user",
            contents=[
                Content.from_text("How old you have to be to drive in Florida?"),
                Content.from_uri(uri=data_uri, media_type="application/pdf", name=os.path.basename(path)),
                # the name parameter is used to specify the filename of the PDF and it is mandatory 
                # even though the content itself already contains the PDF data.
            ],
        )
    )

    print(pdfresponse)

    usage = pdfresponse.usage_details
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
