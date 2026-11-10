import asyncio
import os
from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
from foundry_local_sdk import Configuration, FoundryLocalManager

MODEL_ALIAS = "phi-4-mini"

async def main():
    FoundryLocalManager.initialize(Configuration(
        app_name="maf_foundry_local_demo",
        model_cache_dir=os.path.expanduser(r"~\.foundry\cache\models"),
    ))
    manager = FoundryLocalManager.instance

    # Register hardware execution providers (GPU/NPU) so their variants become eligible
    manager.download_and_register_eps()

    # Resolve the alias to the best variant for this machine (NPU > GPU > CPU)
    model = manager.catalog.get_model(MODEL_ALIAS)
    print(f"Using model variant: {model.id}")
    model.download(lambda p: print(f"\rDownloading: {p:.1f}%", end="", flush=True))
    print()
    model.load()

    manager.start_web_service()

    client = OpenAIChatCompletionClient(
        model=model.id,
        api_key="not-needed",
        base_url=f"{manager.urls[0]}/v1",
    )

    agent = Agent(
        client=client,
        name="Foundry Local Agent",
        instructions="You are a helpful assistant.",
    )

    response = await agent.run("Why is the sky blue?")
    print(response)

    manager.stop_web_service()
    model.unload()

if __name__ == "__main__":
    asyncio.run(main())