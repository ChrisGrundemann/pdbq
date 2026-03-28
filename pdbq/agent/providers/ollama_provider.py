# pdbq - Natural language query agent for PeeringDB
# Copyright (C) 2025 Chris Grundemann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""Ollama model provider (via OpenAI-compatible API)."""
import json

import openai

from pdbq.agent.providers.base import ModelProvider, ToolCall, ToolResult


def _ollama_api_call(fn, base_url: str, model: str):
    """Call fn(), translating connection/model errors into RuntimeError."""
    try:
        return fn()
    except openai.NotFoundError:
        raise RuntimeError(f"Ollama model '{model}' not found. Run: ollama pull {model}")
    except (openai.APIConnectionError, ConnectionRefusedError) as exc:
        raise RuntimeError(
            f"Cannot connect to Ollama at {base_url}. "
            f"Is it running? Try: systemctl start ollama  or  ollama serve"
        ) from exc


def _to_openai_tools(tools: list[dict]) -> list[dict]:
    """Convert Anthropic-format tool definitions to OpenAI function format."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t["input_schema"],
            },
        }
        for t in tools
    ]


class OllamaProvider(ModelProvider):
    def __init__(self, base_url: str, model: str) -> None:
        self._client = openai.OpenAI(
            base_url=f"{base_url}/v1",
            api_key="ollama",
        )
        self._base_url = base_url
        self._model = model

    def run(
        self,
        system: str,
        messages: list[dict],
        tools: list[dict],
    ) -> tuple[str | None, list[ToolCall], dict]:
        openai_messages = [{"role": "system", "content": system}, *messages]
        openai_tools = _to_openai_tools(tools)

        response = _ollama_api_call(
            lambda: self._client.chat.completions.create(
                model=self._model,
                messages=openai_messages,
                tools=openai_tools,
            ),
            self._base_url,
            self._model,
        )

        message = response.choices[0].message
        raw_tool_calls = message.tool_calls or []

        if not raw_tool_calls:
            assistant_message = {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [],
            }
            return message.content or "", [], assistant_message

        tool_calls = [
            ToolCall(
                id=tc.id,
                name=tc.function.name,
                input=json.loads(tc.function.arguments),
            )
            for tc in raw_tool_calls
        ]

        assistant_message = {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in raw_tool_calls
            ],
        }

        return None, tool_calls, assistant_message

    def build_tool_result_message(self, results: list[ToolResult]) -> list[dict]:
        return [
            {
                "role": "tool",
                "tool_call_id": r.tool_call_id,
                "content": r.content,
            }
            for r in results
        ]
