import asyncio
import os
import textwrap

from agent_framework import Agent, AgentResponse, Message
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework.orchestrations import ConcurrentBuilder
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Equivalent of the .NET user secrets: reads "endpoint" and "apikey" from env vars or a .env file
load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
apikey = os.getenv("AZURE_OPENAI_API_KEY")

openai_client = AsyncOpenAI(
    api_key=apikey,
    base_url=endpoint + "/openai/v1/",
)

# If you don't want to use the APIKey, you can use Bearer token authentication instead
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
# openai_client = AsyncOpenAI(
#     api_key=token_provider,
#     base_url=endpoint + "/openai/v1/",
# )

chat_client = OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client)

legal_agent = Agent(
    client=chat_client,
    name="LegalAgent",
    instructions="You are a legal agent that need to evaluate if a text is legal (use max 250 chars)",
)
spelling_error_agent = Agent(
    client=chat_client,
    name="SpellingErrorAgent",
    instructions="You are a spelling expert (use max 250 chars)",
)

# The default aggregator combines each agent's final reply into a single AgentResponse output
workflow = ConcurrentBuilder(participants=[legal_agent, spelling_error_agent]).build()

patentdoc = textwrap.dedent("""\
    This Software Patent Agreement (“Agreement”) is entered into as of the Effective Date by and 
    between the Patent Holder and the Licensee for the purpose of defining the terms under which 
    the Licensee may utilize certain proprietary software technologies covered by one or more issued 
    or pending patents owned or controlled by the Patent Holder. The Patent Holder hereby grants to 
    the Licensee a limited, non-exclusive, non-transferable, and revocable license to make, use, 
    reproduce, and distribute implementations of the patented software methods solely within the 
    scope of the Licensee’s internal business operations or as otherwise expressly authorized in writing. 
    All rights not expressly granted herein remain reserved by the Patent Holder, including without 
    limitation the right to sublicense, enforce, or otherwise commercially exploit the patented technology.
    The Licensee agrees to comply with all applicable intellectual property laws and acknowledges that any 
    unauthorized reproduction, modification, reverse engineering, or distribution of the patented software 
    beyond the scope of this Agrement shall constitute a material breach and may result in immediate 
    termination of the license rights granted herein. In the event of infringement or suspected misuse 
    of the patented technology, the Patent Holder reserves the right to pursue all remedies available 
    at law or in equity, including injunctive relief and recovery of damages. This Agreement shall be 
    governed by and construed in accordance with the applicable jurisdiction specified by the Patent 
    Holder, and any disputes arising hereunder shall be resolved through binding arbitration or 
    a court of competent jurisdiction as mutually agreed by the parties.  
    """).rstrip("\n")


async def main() -> None:
    messages = [Message(role="user", contents=[patentdoc])]

    result: list[Message] = []

    async for evt in workflow.run(messages, stream=True):
        # The aggregator's output is an AgentResponse holding each agent's final reply
        if evt.type == "output" and isinstance(evt.data, AgentResponse):
            result = evt.data.messages

    for message in (x for x in result if x.role != "user"):
        print(message.author_name or "Unknown")
        print(message.text)


if __name__ == "__main__":
    asyncio.run(main())
