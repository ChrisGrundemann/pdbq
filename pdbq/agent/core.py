"""
Main agent loop using Anthropic tool-use.
"""
import json
import logging
from typing import Any, Dict, Iterator, List, Optional, Tuple

import anthropic

from pdbq.agent.prompts import build_system_prompt
from pdbq.agent.tools import TOOL_DEFINITIONS, dispatch_tool
from pdbq.config import settings

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 10


class AgentResult:
    def __init__(
        self,
        answer: str,
        sql_executed: List[str],
        tool_calls: List[Dict[str, Any]],
    ) -> None:
        self.answer = answer
        self.sql_executed = sql_executed
        self.tool_calls = tool_calls


def run_agent(query: str, google_token: Optional[str] = None) -> AgentResult:
    """
    Run the agent loop for a single query. Stateless — no conversation history.
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    system_prompt = build_system_prompt()

    messages: List[Dict[str, Any]] = [{"role": "user", "content": query}]
    sql_executed: List[str] = []
    tool_calls_log: List[Dict[str, Any]] = []

    for iteration in range(MAX_ITERATIONS):
        logger.debug("Agent iteration %d", iteration + 1)

        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=8096,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Collect any text content from this response turn
        text_blocks = [b for b in response.content if b.type == "text"]
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if not tool_use_blocks:
            # Final answer — no more tool calls
            answer = "\n".join(b.text for b in text_blocks) if text_blocks else ""
            return AgentResult(
                answer=answer,
                sql_executed=sql_executed,
                tool_calls=tool_calls_log,
            )

        # Append assistant message with full content
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool call and collect results
        tool_results = []
        for block in tool_use_blocks:
            tool_name = block.name
            tool_input = block.input

            logger.info("Tool call: %s(%s)", tool_name, json.dumps(tool_input)[:200])
            tool_calls_log.append({"tool": tool_name, "input": tool_input})

            if tool_name == "query_db":
                sql_executed.append(tool_input.get("sql", ""))

            result = dispatch_tool(tool_name, tool_input)

            # Pass google_token through to export_to_sheets if not provided in tool input
            if tool_name == "export_to_sheets" and google_token and "user_token" not in tool_input:
                tool_input["user_token"] = google_token
                result = dispatch_tool(tool_name, tool_input)

            tool_calls_log[-1]["result"] = result

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, default=str),
                }
            )

        messages.append({"role": "user", "content": tool_results})

    logger.warning("Agent hit max iterations (%d) without a final answer", MAX_ITERATIONS)
    return AgentResult(
        answer="The agent reached the maximum number of iterations without producing a final answer. Please try a more specific query.",
        sql_executed=sql_executed,
        tool_calls=tool_calls_log,
    )


def stream_agent(query: str, google_token: Optional[str] = None) -> Iterator[str]:
    """
    Stream the final answer token-by-token. Runs tool-use loop synchronously,
    then streams only the final response.
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    system_prompt = build_system_prompt()

    messages: List[Dict[str, Any]] = [{"role": "user", "content": query}]

    for iteration in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=8096,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if not tool_use_blocks:
            # Final answer — stream it
            text_blocks = [b for b in response.content if b.type == "text"]
            full_text = "\n".join(b.text for b in text_blocks)
            # Simulate streaming by yielding the full text
            # For true streaming, use the streaming API on the final call
            yield full_text
            return

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in tool_use_blocks:
            result = dispatch_tool(block.name, block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, default=str),
                }
            )

        messages.append({"role": "user", "content": tool_results})

    yield "The agent reached the maximum number of iterations without producing a final answer."
