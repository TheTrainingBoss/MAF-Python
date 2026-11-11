from dataclasses import dataclass
import msvcrt
from uuid import uuid4
from dotenv import load_dotenv
from agent_framework import VectorStoreField, vectorstoremodel, Agent
from agent_framework.azure import AzureAISearchStore
from agent_framework.openai import OpenAIEmbeddingClient, OpenAIChatClient
from azure.core.credentials import AzureKeyCredential
import asyncio
import os
from openai import AsyncOpenAI
from typing import Annotated, Any
from datetime import datetime, timezone
from collections.abc import Sequence
import math

@dataclass
class KnowledgeBaseEntry:
    question: str
    answer: str


# storage_name values match the C# property names so both demos share the same "agindex" schema
@vectorstoremodel
@dataclass
class KnowledgeBaseVectorRecord:
    id: Annotated[str, VectorStoreField("key", storage_name="Id")]
    question: Annotated[str, VectorStoreField("data", storage_name="Question")]
    answer: Annotated[str, VectorStoreField("data", storage_name="Answer")]
    vector: Annotated[
        str | list[float] | None,
        VectorStoreField("vector", dimensions=1536, storage_name="Vector"),
    ] = None

    def __post_init__(self) -> None:
        if self.vector is None:
            self.vector = f"Q: {self.question} - A: {self.answer}"


async def main():
    load_dotenv()

    client = AsyncOpenAI(
        api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        base_url=os.getenv('AZURE_OPENAI_ENDPOINT') + "/openai/v1/",
        timeout=60,
    )
    # If you don't want to use the APIKey, you can use Entra ID authentication instead
    # from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    # token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
    # client = AsyncOpenAI(
    #     api_key=token_provider,
    #     base_url=endpoint + "/openai/v1/",
    #     timeout=60,
    # )

    embedding_generator = OpenAIEmbeddingClient(
            model="text-embedding-3-small",
            async_client=client,
        )

    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

    # Using Azure AI Search
    async with AzureAISearchStore(
        endpoint=search_endpoint,
        credential=AzureKeyCredential(search_api_key),
        embedding_generator=embedding_generator,
    ) as vector_store_from_azure_ai_search:
        vector_store_collection = vector_store_from_azure_ai_search.get_collection(
            KnowledgeBaseVectorRecord, collection_name=search_index_name
        )

        # Create Agent
        agent = Agent(
            client=OpenAIChatClient(model="gpt-5", async_client=client),
            instructions="You are an expert in the company's Internal Knowledge Base",
        )

        session = agent.create_session()

        while True:
            question = input("Your question: ")

            most_similar_knowledge: list[str] = []
            async for search_result in await vector_store_collection.search(
                question, top=3
            ):
                record = search_result["record"]
                search_result_as_q_and_a = (
                    f"Q: {record.question} - A: {record.answer}"
                )
                print(
                    f"Search result [Score: {search_result['score']}] "
                    f"{search_result_as_q_and_a}"
                )
                most_similar_knowledge.append(search_result_as_q_and_a)

            prompt = (
                "Here is the most relevant Knowledge base information: "
                + "\n".join(most_similar_knowledge)
                + "\n\n"
                + question
            )
            response = await agent.run(prompt, session=session)
            print("Final Answer after Search + LLM")
            print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
