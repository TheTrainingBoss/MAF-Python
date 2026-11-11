import asyncio
import json
import os

from agent_framework import Agent, AgentResponse, AgentResponseUpdate, Message, Workflow
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework.orchestrations import HandoffAgentUserRequest, HandoffBuilder
from dotenv import load_dotenv
from openai import AsyncOpenAI

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

# require_per_service_call_history_persistence keeps each agent's handoff tool calls in its history,
# as recommended for agents taking part in a Python handoff workflow
supervisor = Agent(
    client=OpenAIChatCompletionClient(model="gpt-5-mini", async_client=openai_client),
    name="Supervisor",
    instructions="Determine what type of question was asked. Never answer yourself",
    require_per_service_call_history_persistence=True,
)

movie_connesseur = Agent(
    client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
    name="MovieConnesseur",
    instructions="You are a Movie Connesseur",
    require_per_service_call_history_persistence=True,
)
music_connesseur = Agent(
    client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
    name="MusicConnesseur",
    instructions="You are a Music Connesseur",
    require_per_service_call_history_persistence=True,
)


def build_workflow() -> Workflow:
    return (
        HandoffBuilder(participants=[supervisor, movie_connesseur, music_connesseur])
        .with_start_agent(supervisor)
        .add_handoff(supervisor, [movie_connesseur, music_connesseur])
        .add_handoff(movie_connesseur, [supervisor])
        .add_handoff(music_connesseur, [supervisor])
        .build()
    )


async def run_workflow(workflow: Workflow, messages: list[Message]) -> list[Message]:
    last_executor_id: str | None = None
    result: list[Message] = []
    pending_calls: dict[str, tuple[str, str]] = {}

    stream = workflow.run(messages, stream=True)
    while stream is not None:
        pending_requests = []
        async for event in stream:
            match event.type:
                case "output" if isinstance(event.data, AgentResponseUpdate):
                    update = event.data
                    if event.executor_id != last_executor_id:
                        last_executor_id = event.executor_id
                        print()
                        print(update.author_name or event.executor_id)

                    print(update.text, end="", flush=True)
                    for content in update.contents:
                        # Streamed function calls arrive in chunks (name first, then argument fragments),
                        # so accumulate them per call_id and print once the call's result arrives
                        if content.type == "function_call":
                            name, args = pending_calls.get(content.call_id, ("", ""))
                            pending_calls[content.call_id] = (name or content.name, args + (content.arguments or ""))
                        elif content.type == "function_result" and content.call_id in pending_calls:
                            name, args = pending_calls.pop(content.call_id)
                            print()
                            print(f"Call '{name}' with arguments: {json.dumps(json.loads(args or '{}'))}")

                case "output" if isinstance(event.data, AgentResponse):
                    # Non-streamed agent responses (printed the same way, all at once)
                    for message in event.data.messages:
                        if message.text:
                            print()
                            print(message.author_name or event.executor_id)
                            print(message.text, end="", flush=True)

                case "output" if isinstance(event.data, list):
                    # The final output of the handoff workflow is the whole conversation
                    result = [m for m in event.data if isinstance(m, Message)]

                case "request_info" if isinstance(event.data, HandoffAgentUserRequest):
                    # An agent answered without handing off and the workflow now waits for the user
                    pending_requests.append(event)

                case "executor_failed":
                    print(f"Error in agent {event.executor_id}: {event.data.error_type}: {event.data.message}")

        stream = (
            workflow.run(responses={r.request_id: HandoffAgentUserRequest.terminate() for r in pending_requests},
                         stream=True)
            if pending_requests
            else None
        )

    return result


async def main() -> None:
    while True:
        messages: list[Message] = []
        workflow = build_workflow()
        print()
        messages.append(Message(role="user", contents=[input("> ")]))
        messages.extend(await run_workflow(workflow, messages))


if __name__ == "__main__":
    asyncio.run(main())
