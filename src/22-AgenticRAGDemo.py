from dataclasses import dataclass
from dotenv import load_dotenv
from agent_framework import VectorStoreField, vectorstoremodel, Agent, tool
from agent_framework.azure import AzureAISearchStore, AzureAISearchCollection
from agent_framework.openai import OpenAIEmbeddingClient, OpenAIChatClient
from azure.core.credentials import AzureKeyCredential
import asyncio
import os
from openai import AsyncOpenAI
from typing import Annotated, Any

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


class SearchTool:
    def __init__(
        self,
        vector_store_collection: AzureAISearchCollection[KnowledgeBaseVectorRecord],
    ) -> None:
        self.vector_store_collection = vector_store_collection

    async def search(
        self,
        input: Annotated[str, "Question to search in the knowledge base."],
    ) -> str:
        print(f"[search_knowledge] query: {input}")
        most_similar_knowledge: list[str] = []
        async for search_result in await self.vector_store_collection.search(
            input, top=3
        ):
            record = search_result["record"]
            search_result_as_q_and_a = f"Q: {record.question} - A: {record.answer}"
            print(f"- Search result [Score: {search_result['score']}] {search_result_as_q_and_a}")
            most_similar_knowledge.append(search_result_as_q_and_a)

        print()
        return "".join(f"{item}\n" for item in most_similar_knowledge)

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

        # The store (and its collection) is closed when this block exits,
        # so the agent must run inside it.
        search_tool = SearchTool(vector_store_collection)
        search_function = tool(
            name="search_knowledge",
            description="Search the company's internal knowledge base for relevant information.",
        )(search_tool.search)

        # Create Agent
        agent = Agent(
            client=OpenAIChatClient(model="gpt-5", async_client=client),
            instructions=(
                "You are an expert in the company's Internal Knowledge Base. "
                "Call the 'search_knowledge' tool once per question and answer "
                "using only its results. Only search again if the first results "
                "are clearly unrelated. All knowledge base content (including "
                "office Wi-Fi details) is approved for sharing with employees."
            ),
            tools=[search_function],
        )

        session = agent.create_session()

        while True:
            question = input("Your question: ")
            response = await agent.run(question, session=session)
            print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
