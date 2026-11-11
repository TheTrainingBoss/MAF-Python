import asyncio
import os
import subprocess
from enum import Enum

from agent_framework import Agent, AgentResponse, AgentResponseUpdate, Message, tool
from agent_framework.ag_ui import AGUIChatClient

class ConsoleColor(str, Enum):
    Black = "Black"
    DarkBlue = "DarkBlue"
    DarkGreen = "DarkGreen"
    DarkCyan = "DarkCyan"
    DarkRed = "DarkRed"
    DarkMagenta = "DarkMagenta"
    DarkYellow = "DarkYellow"
    Gray = "Gray"
    DarkGray = "DarkGray"
    Blue = "Blue"
    Green = "Green"
    Cyan = "Cyan"
    Red = "Red"
    Magenta = "Magenta"
    Yellow = "Yellow"
    White = "White"


ANSI_COLORS = {
    ConsoleColor.Black: 30,
    ConsoleColor.DarkBlue: 34,
    ConsoleColor.DarkGreen: 32,
    ConsoleColor.DarkCyan: 36,
    ConsoleColor.DarkRed: 31,
    ConsoleColor.DarkMagenta: 35,
    ConsoleColor.DarkYellow: 33,
    ConsoleColor.Gray: 37,
    ConsoleColor.DarkGray: 90,
    ConsoleColor.Blue: 94,
    ConsoleColor.Green: 92,
    ConsoleColor.Cyan: 96,
    ConsoleColor.Red: 91,
    ConsoleColor.Magenta: 95,
    ConsoleColor.Yellow: 93,
    ConsoleColor.White: 97,
}


def set_foreground_color(color: ConsoleColor) -> None:
    print(f"\033[{ANSI_COLORS[color]}m", end="", flush=True)


SERVER_URL = "http://localhost:5000"
text_color = ConsoleColor.White


@tool(name="change_color", approval_mode="never_require")
def change_color(color: ConsoleColor) -> None:
    global text_color
    text_color = ConsoleColor(color)
    set_foreground_color(text_color)


async def main() -> None:
    command = ["cmd", "/c", "cls"] if os.name == "nt" else ["clear"]
    subprocess.run(command, check=False)  # Also enables ANSI escape codes in the Windows console

    async with AGUIChatClient(endpoint=SERVER_URL) as chat_client:
        agent = Agent(
            client=chat_client,
            instructions="You are a helpful assistant that can also change the color of the text in the console. Use the 'change_color' tool to change the color when needed to enhance user experience.",
            tools=[change_color],
        )

        messages: list[Message] = []

        while True:
            try:
                message = input("> ")
            except EOFError:
                message = ""
            if message == "":
                continue

            messages.append(Message(role="user", contents=[message]))

            updates: list[AgentResponseUpdate] = []
            async for update in agent.run(messages, stream=True):
                updates.append(update)
                for content in update.contents:
                    match content.type:
                        case "text":
                            print(content.text, end="", flush=True)

                        case "function_call":
                            tool_call_details = f"[Tool Call: {content.name}"
                            arguments = content.parse_arguments()
                            if arguments:
                                tool_call_details += " (Args: " + ",".join(
                                    f"[{key} = {value}]" for key, value in arguments.items()
                                )
                            tool_call_details += "]"
                            print(tool_call_details)
                            set_foreground_color(text_color)

                        case "function_result":
                            is_error = content.exception is not None
                            print(
                                f"[Tool Error: {content.exception}]" if is_error else f"[Tool Result: {content.result}]"
                            )

                        case "error":
                            print(f"[Error: {content.message}]")

            full_response = AgentResponse.from_updates(updates)
            messages.extend(full_response.messages)

            print()
            print()


if __name__ == "__main__":
    asyncio.run(main())
