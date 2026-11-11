import os

import uvicorn
from agent_framework import Agent, tool
from agent_framework.ag_ui import add_agent_framework_fastapi_endpoint
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from fastapi import FastAPI
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


# Server-Tool
@tool(name="get_weather", approval_mode="never_require")
def get_weather(city: str) -> str:
    return "It is sunny and 72 degrees"


agent = Agent(
    client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
    tools=[get_weather],
)

# AG-UI Part begin
app = FastAPI()

# Local demo only: single-user mode does not authenticate callers.
# In production, you would implement proper authentication and authorization for the AG-UI endpoint
# using authorization scope resolver for shared applications.
add_agent_framework_fastapi_endpoint(app, agent, "/", single_user=True)

if __name__ == "__main__":
    # Same default address as ASP.NET Core (http://localhost:5000)
    uvicorn.run(app, host="localhost", port=5000)
