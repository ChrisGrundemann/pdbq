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
"""Anthropic model provider."""
import anthropic

from pdbq.agent.providers.base import ModelProvider, ToolCall, ToolResult


class AnthropicProvider(ModelProvider):
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when MODEL_PROVIDER=anthropic")
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def run(
        self,
        system: str,
        messages: list[dict],
        tools: list[dict],
    ) -> tuple[str | None, list[ToolCall], dict]:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=8096,
            system=system,
            tools=tools,
            messages=messages,
        )

        assistant_message = {"role": "assistant", "content": response.content}
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if not tool_use_blocks:
            text_blocks = [b for b in response.content if b.type == "text"]
            answer = "\n".join(b.text for b in text_blocks) if text_blocks else ""
            return answer, [], assistant_message

        tool_calls = [
            ToolCall(id=b.id, name=b.name, input=b.input)
            for b in tool_use_blocks
        ]
        return None, tool_calls, assistant_message

    def build_tool_result_message(self, results: list[ToolResult]) -> list[dict]:
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": r.tool_call_id,
                        "content": r.content,
                    }
                    for r in results
                ],
            }
        ]
