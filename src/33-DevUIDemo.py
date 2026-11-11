import os

from agent_framework import Agent, tool
from agent_framework.devui import serve
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework.orchestrations import ConcurrentBuilder, SequentialBuilder
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


@tool(name="GetWeather", approval_mode="never_require")
def get_weather(city: str) -> str:
    return "It is sunny and 72 degrees"


chat_client = OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client)

egyptian_king = Agent(
    client=chat_client,
    name="The Egyptian King",
    instructions="You are an Egyptian Pharaoh and you speak like one",
    tools=[get_weather],
)

pirate_agent = Agent(
    client=chat_client,
    name="The Pirate of the High Seas",
    instructions="Speak like a pirate",
    tools=[get_weather],
)

# Sample workflows
french_translator = Agent(
    client=chat_client, name="french-translator", instructions="Translate any text you get into French"
)
arabic_translator = Agent(
    client=chat_client, name="arabic-translator", instructions="Translate any text you get into Arabic"
)

translation_workflow_sequential = SequentialBuilder(
    name="translation-workflow-sequential",
    participants=[french_translator, arabic_translator],
).build()

translation_workflow_concurrent = ConcurrentBuilder(
    name="translation-workflow-concurrent",
    participants=[french_translator, arabic_translator],
).build()


if __name__ == "__main__":
    serve(
        entities=[
            egyptian_king,
            pirate_agent,
            french_translator,
            arabic_translator,
            translation_workflow_sequential,
            translation_workflow_concurrent,
        ],
        port=5266,
        auto_open=True,
        auth_enabled=False  # Disable authentication for the DevUI server otherwise you need to get a bearer token to authenticate.

        # Run the following in the terminal to get a token:
        # $env:DEVUI_AUTH_TOKEN = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
        # $env:DEVUI_AUTH_TOKEN
        # .\.venv\Scripts\python.exe .\src\33-DevUIDemo.py
    )
