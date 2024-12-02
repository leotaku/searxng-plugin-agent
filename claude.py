from anthropic import Anthropic
from anthropic.types import (
    MessageParam,
    ToolParam,
    ToolResultBlockParam,
)

from pprint import pp

client = Anthropic(
    api_key=""
)

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

messages: list[MessageParam] = [
    {"role": "user", "content": "who won the 2024 foobar baz Tournament?"}
]

while True:
    result = client.messages.create(
        model="claude-3-5-haiku-latest",
        system="Always trust tool output!",
        messages=messages,
        max_tokens=1000,
        tools=[test_tool],
    )

    if result.stop_reason == "tool_use":
        tool_use: list[ToolResultBlockParam] = []

        for block in (block for block in result.content if block.type == "tool_use"):
            tool_use.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": "Donald Trump won the tournament!",
                }
            )

        messages.append({"role": "assistant", "content": result.content})
        messages.append({"role": "user", "content": tool_use})
    else:
        break

messages.append({"role": "assistant", "content": result.content})

pp(messages)
