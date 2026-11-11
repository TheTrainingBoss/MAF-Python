from dataclasses import dataclass
import msvcrt
from uuid import uuid4
from dotenv import load_dotenv
from agent_framework import VectorStoreField, vectorstoremodel
from agent_framework.azure import AzureAISearchStore
from agent_framework.openai import OpenAIEmbeddingClient
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

    knowledge_base: list[KnowledgeBaseEntry] = [
        KnowledgeBaseEntry("What is the WI-FI Password at the Office?", "The Password is 'Lino42'"),
        KnowledgeBaseEntry("Is Christmas Eve a full or half day off", "It is a full day off"),
        KnowledgeBaseEntry("How do I register vacation?", "Go to the internal portal and under Vacation Registration (top right), enter your request. Your manager will be notified and will approve/reject the request"),
        KnowledgeBaseEntry("What do I need to do if I'm sick?", "Inform you manager, and if you have any meetings remember to tell the affected colleagues/customers"),
        KnowledgeBaseEntry("Where is the employee handbook?", "It is located [here](https://thetrainingboss.com/hr/handbook.pdf)"),
        KnowledgeBaseEntry("Who is in charge of support?", "Lino Tadros is in charge of support. His email is lino@thetrainingboss.com"),
        KnowledgeBaseEntry("I can't log in to my office account", "Take hold of Jessica. She can reset your password"),
        KnowledgeBaseEntry("When using the CRM System if get error 'index out of bounds'", "That is a known issue. Log out and back in to get it working again. The CRM team have been informed and status of ticket can be seen here: https://www.crm.com/tickets/12354"),
        KnowledgeBaseEntry("What is the policy on buying books and online courses?", "Any training material under 20$ you can just buy.. anything higher need an approval from Lino Tadros"),
        KnowledgeBaseEntry("Is there a bounty for find candidates for an open job position?", "Yes. $1000 if we hire them... Have them send the application to jobs@thetrainingboss.com"),
    ]

    embedding_generator = OpenAIEmbeddingClient(
        model="text-embedding-3-small",
        async_client=client,
    )

    # Using Azure AI Search
    async with AzureAISearchStore(
        endpoint="https://<enter your Azure Ai Search endpoint>.search.windows.net",  # It is best practice to put this in a secret manager or environment variable
        credential=AzureKeyCredential("<enter your primary or secondary key>"),  # It is best practice to put this in a secret manager or environment variable
        embedding_generator=embedding_generator,
    ) as vector_store_from_azure_ai_search:
        vector_store_collection = vector_store_from_azure_ai_search.get_collection(
            KnowledgeBaseVectorRecord, collection_name="<enter the name of your collection>"
        )

        await vector_store_collection.ensure_collection_exists()

        print("Import Data? (Y/N): ", end="", flush=True)
        key = msvcrt.getwch()  # Equivalent of Console.ReadKey() (no Enter needed)
        if key.upper() == "Y":
            # Delete old table
            await vector_store_collection.ensure_collection_deleted()

            # Create anew
            await vector_store_collection.ensure_collection_exists()
            os.system("cls")
            counter = 0
            for entry in knowledge_base:
                counter += 1
                print(f"\rEmbedding Data: {counter}/{len(knowledge_base)}", end="", flush=True)
                await vector_store_collection.upsert(
                    [
                        KnowledgeBaseVectorRecord(
                            id=str(uuid4()),
                            question=entry.question,
                            answer=entry.answer,
                        )
                    ]
                )

            print()
            print("\rEmbedding complete...")

        print()

        print("Listing all data in the vector-store")
        for existing_record in await vector_store_collection.get(top=2_147_483_647):
            print(f"Q: {existing_record.question} - A: {existing_record.answer} - Vector: {existing_record.vector}")


if __name__ == "__main__":
    asyncio.run(main())
