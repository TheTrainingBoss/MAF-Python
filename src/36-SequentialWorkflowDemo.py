import asyncio
import os
import textwrap

from agent_framework import Agent, AgentResponse, AgentResponseUpdate, Message
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework.orchestrations import SequentialBuilder
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

summary_agent = Agent(
    client=chat_client, 
    name="SummaryAgent", 
    instructions="Summarize the text you are given to max 25 words"
)
translation_agent = Agent(
    client=chat_client,
    name="TranslationAgent",
    instructions="Given some text, Translate it to French (you need to translate the summary and not the original text)",
)

workflow = SequentialBuilder(participants=[summary_agent, translation_agent], 
                             output_from="all").build()

# I could have built the workflow by adding executors and connecting them
# workflow = WorkflowBuilder(start_executor=summary_agent).add_edge(summary_agent, translation_agent).build()

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
    beyond the scope of this Agreement shall constitute a material breach and may result in immediate 
    termination of the license rights granted herein. In the event of infringement or suspected misuse 
    of the patented technology, the Patent Holder reserves the right to pursue all remedies available 
    at law or in equity, including injunctive relief and recovery of damages. This Agreement shall be 
    governed by and construed in accordance with the applicable jurisdiction specified by the Patent 
    Holder, and any disputes arising hereunder shall be resolved through binding arbitration or 
    a court of competent jurisdiction as mutually agreed by the parties.  
    """).rstrip("\n")


async def main() -> None:
    messages = [Message(role="user", contents=[patentdoc])]

    updates_by_agent: dict[str, list[AgentResponseUpdate]] = {}

    async for evt in workflow.run(messages, stream=True):
        # In streaming mode, each agent's output arrives as a series of AgentResponseUpdate chunks
        if evt.type == "output" and isinstance(evt.data, AgentResponseUpdate):
            updates_by_agent.setdefault(evt.executor_id, []).append(evt.data)

    # Combine each agent's chunks into its full response, giving the conversation as a list of messages
    result: list[Message] = [
        message for updates in updates_by_agent.values() for message in AgentResponse.from_updates(updates).messages
    ]

    for message in (x for x in result if x.role != "user"):
        print(message.text)


if __name__ == "__main__":
    asyncio.run(main())
