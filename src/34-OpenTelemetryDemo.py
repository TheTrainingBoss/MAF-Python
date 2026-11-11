import asyncio
import os

from agent_framework import Agent
from agent_framework.observability import enable_sensitive_telemetry
from agent_framework.openai import OpenAIChatCompletionClient
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from dotenv import load_dotenv
from openai import AsyncOpenAI
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import set_tracer_provider

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
apikey = os.getenv("AZURE_OPENAI_API_KEY")
appinsightsConnectionString = os.getenv("APPLICATION_INSIGHTS_INSTRUMENTATION_KEY")

# Setup Telemetry
source_name = "agentframework-opentelemetry-demo"
tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: source_name}))
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
if appinsightsConnectionString.strip():
    tracer_provider.add_span_processor(
        BatchSpanProcessor(AzureMonitorTraceExporter(connection_string=appinsightsConnectionString))
    )
set_tracer_provider(tracer_provider)

# Agent Framework instruments agents and chat clients automatically (no UseOpenTelemetry wrapper needed).
# Be careful with this in production, it can leak personally identifiable information. Use only if you are sure you
# won't log sensitive data, or if you have proper safeguards in place to protect the telemetry data
enable_sensitive_telemetry()

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

agent = Agent(
    client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
    name="MyLogAnalyticsAgent",
    instructions="You are a knowledgeable assistant that helps answer questions. Always try to be helpful, precise and concise in your answers. If you don't know the answer, say you don't know instead of trying to make something up.",
)


async def main() -> None:
    session = agent.create_session()

    response = await agent.run("Why is the sky blue?", session=session)
    print(response.text)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # flushes pending spans to the exporters
        tracer_provider.shutdown()

#  KQL query to analyze OpenTelemetry data in Azure Monitor
#  dependencies
#  | extend cd = parse_json(customDimensions)
#  |project
#      timestamp,
#      id,
#      duration,
#      InTokens = cd["gen_ai.usage.input_tokens"],
#      OutTokens = cd["gen_ai.usage.output_tokens"],
#      AgentName = cd["gen_ai.agent.name"],
#      AIModel = cd["gen_ai.response.model"],
#      InputData = cd["gen_ai.input.messages"],
#      OutputData = cd["gen_ai.output.messages"]
