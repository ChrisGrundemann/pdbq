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
"""Abstract base for model providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict  # always a parsed dict, never a raw JSON string


@dataclass
class ToolResult:
    tool_call_id: str
    content: str


class ModelProvider(ABC):
    @abstractmethod
    def run(
        self,
        system: str,
        messages: list[dict],
        tools: list[dict],
    ) -> tuple[str | None, list[ToolCall], dict]:
        """Send one turn to the model.

        Returns (final_answer, [], assistant_message) when the model produces
        no tool calls, or (None, tool_calls, assistant_message) when the model
        wants tools executed. The assistant_message dict is always ready to
        append to the history.
        """

    @abstractmethod
    def build_tool_result_message(self, results: list[ToolResult]) -> list[dict]:
        """Wrap tool results as message dicts to extend the history with."""
