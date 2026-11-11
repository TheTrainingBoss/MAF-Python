import asyncio
import os
import uuid
from typing import Any

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient, OpenAIEmbeddingClient
from azure.cosmos.aio import ContainerProxy, CosmosClient
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Equivalent of the .NET user secrets: reads these values from env vars or a .env file
load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
apikey = os.getenv("AZURE_OPENAI_API_KEY")
cosmosEndpoint = os.getenv("COSMOS_ENDPOINT")
cosmosKey = os.getenv("COSMOS_API_KEY")
cosmosDatabase = os.getenv("COSMOS_DATABASE_NAME")
cosmoscachecontainer = os.getenv("COSMOS_CACHE_CONTAINER_NAME")

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

embedding_generator = OpenAIEmbeddingClient(model="text-embedding-3-small", async_client=openai_client)

agent = Agent(client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client))


async def find_similar(container: ContainerProxy, embedding: list[float]) -> dict[str, Any] | None:
    query = """
        SELECT TOP 1 c.id, c.question, c.answer, VectorDistance(c.embedding, @embedding) AS similarity
        FROM c
        WHERE c.pk = @pk AND VectorDistance(c.embedding, @embedding) > 0.3
        ORDER BY VectorDistance(c.embedding, @embedding)
    """
    parameters = [
        {"name": "@embedding", "value": embedding},
        {"name": "@pk", "value": "cache"},
    ]

    async for item in container.query_items(query=query, parameters=parameters):
        return item
    return None


async def main() -> None:
    async with CosmosClient(cosmosEndpoint, credential=cosmosKey) as cosmos_client:
        database = cosmos_client.get_database_client(cosmosDatabase)
        container = database.get_container_client(cosmoscachecontainer)

        question = "What are the top 10 Movies according to IMDB?"
        embedding = list((await embedding_generator.get_embeddings([question]))[0].vector)

        session = agent.create_session()

        # Step 1: Check semantic cache
        cached = await find_similar(container, embedding)

        if cached is not None:
            print("Cache HIT, lucky you! no time or money spent on this one :)")
            print(cached["answer"])
            return

        print("Cache MISS → Calling LLM")

        # Step 2: Call agent / LLM
        response = await agent.run(question, session=session)

        # Step 3: Store in cache
        item = {
            "id": str(uuid.uuid4()),
            "pk": "cache",
            "question": question,
            "embedding": embedding,
            "answer": response.text,
        }

        await container.create_item(item)

        print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
