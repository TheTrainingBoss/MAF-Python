import asyncio
import os

from agent_framework import Agent, CompactionProvider, SummarizationStrategy
from agent_framework.azure import CosmosHistoryProvider
from agent_framework.openai import OpenAIChatCompletionClient
from azure.cosmos.aio import CosmosClient
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Equivalent of the .NET user secrets: reads these values from env vars or a .env file
load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
apikey = os.getenv("AZURE_OPENAI_API_KEY")
cosmosdbEndpoint = os.getenv("COSMOS_ENDPOINT")
cosmosdbKey = os.getenv("COSMOS_API_KEY")

conversationId = "LinoConversation"  # This is where you will have to decide on the conversationId strategy that best fits your scenario, it can be a fixed value for single conversation scenarios or something more dynamic like a session id or a combination of tenantId+userId for multi-tenant/multi-user scenarios. The important thing is that this value is used consistently across calls so that the chat history can be retrieved correctly.

# Python history provider uses the name "chathistory-python" for the container and use the /session_id as the partition key automatically.
DATABASE_ID = "ttbcosmosdb"
CONTAINER_ID = "chathistory-python"

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

question = "ok can you give the top 5 only"
# "What are the top 10 Movies according to IMDB?"; 
# "ok can you give the top 5 only";


async def main() -> None:
    async with CosmosClient(cosmosdbEndpoint, credential=cosmosdbKey) as cosmos_client:
        history_provider = CosmosHistoryProvider(
            cosmos_client=cosmos_client,
            database_name=DATABASE_ID,
            container_name=CONTAINER_ID,
        )

        # Summarizes the oldest messages once the conversation exceeds 8 messages (target_count + threshold),
        # equivalent of CompactionTriggers.MessagesExceed(8)
        compaction_strategy = SummarizationStrategy(
            client=OpenAIChatCompletionClient(model="gpt-5-mini", async_client=openai_client),
            target_count=4,
            threshold=4,
        )
        compaction_provider = CompactionProvider(
            before_strategy=compaction_strategy,
            history_source_id=history_provider.source_id,
        )

        # Provider order matters: history loads first, then compaction summarizes what was loaded
        agent = Agent(
            client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
            context_providers=[history_provider, compaction_provider],
        )

        session = agent.create_session(session_id=conversationId)

        response = await agent.run(question, session=session)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
