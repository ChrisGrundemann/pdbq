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
"""
Main agent loop using provider abstraction.
"""
import json
import logging
from typing import Any, Dict, Iterator, List, Optional

from pdbq.agent.prompts import build_system_prompt
from pdbq.agent.providers.base import ModelProvider, ToolResult
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


def get_provider(api_key: Optional[str] = None) -> ModelProvider:
    if settings.model_provider == "ollama":
        from pdbq.agent.providers.ollama_provider import OllamaProvider
        return OllamaProvider(base_url=settings.ollama_base_url, model=settings.ollama_model)
    else:
        from pdbq.agent.providers.anthropic_provider import AnthropicProvider
        return AnthropicProvider(api_key=api_key or settings.anthropic_api_key or "", model=settings.anthropic_model)


def run_agent(query: str, google_token: Optional[str] = None, api_key: Optional[str] = None) -> AgentResult:
    """
    Run the agent loop for a single query. Stateless — no conversation history.
    """
    provider = get_provider(api_key=api_key)
    system_prompt = build_system_prompt()

    messages: List[Dict[str, Any]] = [{"role": "user", "content": query}]
    sql_executed: List[str] = []
    tool_calls_log: List[Dict[str, Any]] = []

    for iteration in range(MAX_ITERATIONS):
        logger.debug("Agent iteration %d", iteration + 1)

        answer, tool_calls, assistant_message = provider.run(system_prompt, messages, TOOL_DEFINITIONS)

        if not tool_calls:
            return AgentResult(
                answer=answer or "",
                sql_executed=sql_executed,
                tool_calls=tool_calls_log,
            )

        messages.append(assistant_message)

        tool_results = []
        for tc in tool_calls:
            logger.info("Tool call: %s(%s)", tc.name, json.dumps(tc.input)[:200])
            tool_calls_log.append({"tool": tc.name, "input": tc.input})

            # Graceful early exit — agent has determined query is out of scope
            if tc.name == "decline_query":
                reason = tc.input.get("reason", "This question is outside pdbq's scope.")
                return AgentResult(
                    answer=reason,
                    sql_executed=sql_executed,
                    tool_calls=tool_calls_log,
                )

            if tc.name == "query_db":
                sql_executed.append(tc.input.get("sql", ""))

            tool_input = tc.input

            # Pass google_token through to export_to_sheets if not provided in tool input
            if tc.name == "export_to_sheets" and google_token and "user_token" not in tool_input:
                tool_input = {**tool_input, "user_token": google_token}

            result = dispatch_tool(tc.name, tool_input, api_key=api_key)
            tool_calls_log[-1]["result"] = result

            tool_results.append(
                ToolResult(
                    tool_call_id=tc.id,
                    content=json.dumps(result, default=str),
                )
            )

        messages.extend(provider.build_tool_result_message(tool_results))

    logger.warning("Agent hit max iterations (%d) without a final answer", MAX_ITERATIONS)
    return AgentResult(
        answer="The agent reached the maximum number of iterations without producing a final answer. Please try a more specific query.",
        sql_executed=sql_executed,
        tool_calls=tool_calls_log,
    )


def stream_agent(query: str, google_token: Optional[str] = None, api_key: Optional[str] = None) -> Iterator[str]:
    """
    Stream the final answer token-by-token. Runs tool-use loop synchronously,
    then streams only the final response.
    """
    provider = get_provider(api_key=api_key)
    system_prompt = build_system_prompt()

    messages: List[Dict[str, Any]] = [{"role": "user", "content": query}]

    for iteration in range(MAX_ITERATIONS):
        answer, tool_calls, assistant_message = provider.run(system_prompt, messages, TOOL_DEFINITIONS)

        if not tool_calls:
            yield answer or ""
            return

        messages.append(assistant_message)

        tool_results = []
        for tc in tool_calls:
            tool_input = tc.input
            if tc.name == "decline_query":
                yield tc.input.get("reason", "This question is outside pdbq's scope.")
                return
            if tc.name == "export_to_sheets" and google_token and "user_token" not in tool_input:
                tool_input = {**tool_input, "user_token": google_token}
            result = dispatch_tool(tc.name, tool_input, api_key=api_key)
            tool_results.append(
                ToolResult(
                    tool_call_id=tc.id,
                    content=json.dumps(result, default=str),
                )
            )

        messages.extend(provider.build_tool_result_message(tool_results))

    yield "The agent reached the maximum number of iterations without producing a final answer."
