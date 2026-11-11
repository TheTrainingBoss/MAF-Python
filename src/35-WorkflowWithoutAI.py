import asyncio
from typing import Never

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler


class UppercaseExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="UppercaseExecutor")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(message.upper())  # The sent message will go along an edge to subsequent executors


class ReverseTextExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="ReverseTextExecutor")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(message[::-1])


async def main() -> None:
    # Create the executors
    uppercase = UppercaseExecutor()
    reverse = ReverseTextExecutor()

    # Build the workflow by connecting executors sequentially
    workflow = WorkflowBuilder(start_executor=uppercase).add_edge(uppercase, reverse).build()

    # Execute the workflow in streaming mode
    async for evt in workflow.run("Hello, World!", stream=True):
        if evt.type == "executor_completed":
            # Python reports what the executor sent/yielded as a list
            data = ", ".join(str(item) for item in evt.data or [])
            print(f"{evt.executor_id}: {data}")


if __name__ == "__main__":
    asyncio.run(main())
