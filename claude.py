from typing import Any, Generator
from anthropic import Anthropic
from anthropic.types import (
    MessageParam,
    ToolParam,
    ToolUseBlock,
)
import httpx


client = Anthropic()

test_tool: ToolParam = {
    "name": "get_article",
    "description": "A tool to retrieve up to date information from search engines.",
    "input_schema": {
        "type": "object",
        "properties": {
            "search_term": {
                "type": "string",
                "description": "The question to ask.",
            },
        },
        "required": ["search_term"],
    },
}

system = (
    "You are a helpful assistant that lives inside a browser search window. \n"
    + "Keep your response brief, and extremely focused on the query.\n"
    + "If you can respond in just a few words! Ideally just a single sentence!"
    + "Only use tools if you think you need to!"
)


def handle_tool_use(messages: list[MessageParam]) -> tuple[bool, list[MessageParam]]:
    needs_reprocessing = False

    for message in messages:
        for block in message["content"]:
            if isinstance(block, dict) and block["type"] == "tool_use":
                id = block["id"]
                params: Any = block["input"]
            elif isinstance(block, ToolUseBlock):
                id = block.id
                params: Any = block.input
            else:
                continue

            needs_reprocessing = True
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": id,
                            "content": httpx.get(
                                f"http://localhost:8080/search?q={params['search_term']}&format=json"
                            ).text,
                        }
                    ],
                }
            )

    return needs_reprocessing, messages


def stream_anthropic(
    messages: list[MessageParam],
) -> Generator[Any, None, list[MessageParam]]:
    with client.messages.stream(
        model="claude-3-5-sonnet-latest",
        system=system,
        messages=messages,
        max_tokens=1000,
        tools=[test_tool],
        tool_choice={"type": "auto"},
    ) as stream:
        for event in stream:
            match event.type:
                case (
                    "text"
                    | "input_json"
                    | "content_block_start"
                    | "content_block_stop"
                    | "message_start"
                ):
                    yield {"kind": "ping", "data": None}
                case "content_block_delta":
                    match event.delta.type:
                        case "input_json_delta":
                            yield {"kind": "ping", "data": None}
                        case "text_delta":
                            yield {"kind": "update", "data": event.delta.text}
                case "message_stop":
                    messages.append(
                        {"role": "assistant", "content": event.message.content}
                    )

    return messages


messages: list[MessageParam] = [
    {
        "role": "user",
        "content": [{"type": "text", "text": "What is happening with Rene Benko?"}],
    }
]

for _ in range(2):
    try:
        stream = stream_anthropic(messages)
        while True:
            signal = next(stream)
            if signal["kind"] == "update":
                print(signal["data"], end="")
    except StopIteration as result:
        print("\n---")
        retry, messages = handle_tool_use(result.value)
        if not retry:
            break
