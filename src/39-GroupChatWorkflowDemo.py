import asyncio
import json
import os

from agent_framework import Agent, AgentResponseUpdate, Message, Workflow
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework.orchestrations import GroupChatBuilder, GroupChatState
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

movie_connesseur = Agent(
    client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
    name="MovieConnesseur",
    instructions="You are a Movie Connesseur",
)
music_connesseur = Agent(
    client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
    name="MusicConnesseur",
    instructions="You are a Music Connesseur",
)


# RoundRobinGroupChatManager: participants take turns in order.
# You could implement your own selection logic to achieve different group chat behaviors
# (e.g. priority-based turn taking, dynamic turn taking based on message content, etc.)
def round_robin_selector(state: GroupChatState) -> str:
    participant_names = list(state.participants.keys())
    return participant_names[state.current_round % len(participant_names)]


def build_workflow() -> Workflow:
    # A workflow where two artistic agents take turns responding in a round-robin fashion.
    return GroupChatBuilder(
        name="Art Round Robin Workflow",
        participants=[movie_connesseur, music_connesseur],
        selection_func=round_robin_selector,
        max_rounds=3, 
        # Stream each agent's response as it is generated; the full transcript is the final output
        intermediate_output_from=[movie_connesseur, music_connesseur],
    ).build()


async def run_workflow(workflow: Workflow, messages: list[Message]) -> list[Message]:
    last_executor_id: str | None = None

    async for event in workflow.run(messages, stream=True):
        match event.type:
            case "intermediate" | "output" if isinstance(event.data, AgentResponseUpdate):
                update = event.data
                if event.executor_id != last_executor_id:
                    last_executor_id = event.executor_id
                    print()
                    print(update.author_name or event.executor_id)

                print(update.text, end="", flush=True)
                call = next((c for c in update.contents if c.type == "function_call"), None)
                if call is not None:
                    print()
                    print(f"Call '{call.name}' with arguments: {json.dumps(call.parse_arguments())}]")

            case "output" if isinstance(event.data, list):
                # The final output of the group chat is the whole conversation
                return [m for m in event.data if isinstance(m, Message)]

            case "executor_failed":
                print(f"Error in agent {event.executor_id}: {event.data.error_type}: {event.data.message}")

    return []


async def main() -> None:
    while True:
        messages: list[Message] = []
        workflow = build_workflow()

        print()
        messages.append(Message(role="user", contents=[input("> ")]))
        messages.extend(await run_workflow(workflow, messages))


if __name__ == "__main__":
    asyncio.run(main())
