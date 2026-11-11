import asyncio
import os
import random
from dataclasses import dataclass
from typing import Never

from agent_framework import Agent, Executor, WorkflowBuilder, WorkflowContext, handler, response_handler
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

# Equivalent of the .NET user secrets: reads "endpoint" and "apikey" from env vars or a .env file
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

agent = Agent(
    client=OpenAIChatCompletionClient(model="gpt-5", async_client=openai_client),
    instructions="You are the judge in a guessing game where it is about guessing animals. "
    "Each hint should only give one fact",
)


@dataclass
class FeedbackToUser:
    hint: str
    init: bool = False


# Structured output for the "is this the right answer?" question
class IsRightAnswer(BaseModel):
    result: bool


class EvaluateAndHintExecutor(Executor):
    def __init__(self, agent: Agent, animal_to_guess: str) -> None:
        super().__init__(id="Evaluator and Hint-giver")
        self._agent = agent
        self._animal_to_guess = animal_to_guess
        self._number_of_tries = 0
        self._hints_given: list[str] = []

    @handler
    async def start(self, feedback: FeedbackToUser, ctx: WorkflowContext) -> None:
        await ctx.request_info(request_data=feedback, response_type=str)

    @response_handler
    async def handle(self, original_request: FeedbackToUser, message: str, ctx: WorkflowContext[Never, str]) -> None:
        self._number_of_tries += 1
        prompt = (
            f"Is this the right answer for guessing the animal is '{self._animal_to_guess}'? "
            f"(allow for spelling errors of the animal): {message}"
        )
        is_right_answer_response = await self._agent.run(prompt, options={"response_format": IsRightAnswer})
        if is_right_answer_response.value is not None and is_right_answer_response.value.result:
            # End the Game
            await ctx.yield_output(
                f"You guessed it. The answer is indeed a {self._animal_to_guess}. Tries used: {self._number_of_tries}"
            )
        else:
            # Not correct answer: Let's generate a new Hint
            new_hint_prompt = (
                f"Generate a hint for a child to guess the animal '{self._animal_to_guess}'. "
                f"Hints already given: {' | '.join(self._hints_given)} "
                "so make the new hint unique and do not repeat the same hint parts"
            )
            hint_response = await self._agent.run(new_hint_prompt)
            new_hint = hint_response.text
            self._hints_given.append(new_hint)
            await ctx.request_info(request_data=FeedbackToUser(new_hint), response_type=str)


async def main() -> None:
    animals = ["Wolf", "Eagle", "Tiger", "Dolphin", "Elephant", "Grizzly Bear", "Mouse", "Dog", "Shark", "Panda"]

    animal_to_guess = random.choice(animals)
    initial_hint_response = await agent.run(f"Make a vague hint for the animal: '{animal_to_guess}'")

    evaluate_and_hint_executor = EvaluateAndHintExecutor(agent, animal_to_guess)
    workflow = WorkflowBuilder(start_executor=evaluate_and_hint_executor).build()

    initial_feedback = FeedbackToUser(initial_hint_response.text, True)
    stream = workflow.run(initial_feedback, stream=True)

    while stream is not None:
        responses: dict[str, str] = {}
        async for evt in stream:
            if evt.type == "request_info":
                if isinstance(evt.data, FeedbackToUser):
                    feedback_to_user = evt.data
                    print(
                        "Guess what animal I'm thinking of"
                        if feedback_to_user.init
                        else "That is not the animal I'm thinking of"
                    )
                    print(f"Hint: {feedback_to_user.hint}")
                    print("-" * 50)
                    responses[evt.request_id] = input("Your Guess: ")
                else:
                    raise NotImplementedError(f"Request {type(evt.data).__name__} is not supported")
            elif evt.type == "output":
                print(evt.data)
                return

        # Send the guess back to the workflow, which resumes in the executor's @response_handler
        stream = workflow.run(responses=responses, stream=True) if responses else None


if __name__ == "__main__":
    asyncio.run(main())
