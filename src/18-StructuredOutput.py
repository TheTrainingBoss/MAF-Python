from dotenv import load_dotenv
from agent_framework.openai import OpenAIChatClient
from agent_framework import Agent, FunctionInvocationContext, function_middleware, tool
import asyncio
import os
from openai import AsyncOpenAI
from pydantic import BaseModel
from enum import Enum
from typing import Any
from datetime import datetime, timezone

async def main():
    load_dotenv()

    # AsyncOpenAI comes from the openai package. 
    # It's the OpenAI SDK's low-level async HTTP client.
    client = AsyncOpenAI(
        api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        base_url=os.getenv('AZURE_OPENAI_ENDPOINT') + "/openai/v1/",
        timeout=60,
    )

    question = "What are the top 10 rated Movies according to IMDB?"

    # Without Structured Output
    agent1 = Agent(
        client=OpenAIChatClient(model="gpt-5-mini", async_client=client),
        instructions="You are an expert in IMDB Lists",
    )
    response1 = await agent1.run(question)
   
    # This response is not guaranteed to have a structure format; hence the need for this Structured Output feature
    print(response1)  

    # With Structured Output
    agent2 = Agent(
        client=OpenAIChatClient(model="gpt-5", async_client=client),
        instructions="You are an expert in IMDB Lists",
    )

    response2 = await agent2.run(question, options={"response_format": MovieList})

    movies: list[Movie] = response2.value.movies

    counter = 1
    for movie in movies:
        print(
            f"{counter}: {movie.title} ({movie.year_of_release}) - Genre: {movie.genre.value} "
            f"- Director: {movie.director} - IMDB Score: {movie.imdb_score}"
        )
        counter += 1


class MovieGenre(str, Enum):
    ScienceFiction = "ScienceFiction"
    Drama = "Drama"
    Comedy = "Comedy"
    Horror = "Horror"
    LoveStory = "LoveStory"
    Other = "Other"

class Movie(BaseModel):
    title: str
    year_of_release: int
    director: str
    genre: MovieGenre
    imdb_score: float

#OpenAI structured output requires an object at the root, so List<Movie> is wrapped
class MovieList(BaseModel):
    movies: list[Movie]


if __name__ == "__main__":
    asyncio.run(main())