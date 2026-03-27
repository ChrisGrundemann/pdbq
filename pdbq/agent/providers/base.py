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
