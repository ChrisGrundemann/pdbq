import json
import os
import time
from typing import Any, Dict, Iterator, Optional

import anthropic
from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse

from pdbq.agent.core import run_agent
from pdbq.agent.tools import TOOL_DEFINITIONS, dispatch_tool
from pdbq.api.auth import require_api_key
from pdbq.api.models import QueryRequest, QueryResponse
from pdbq.config import settings

router = APIRouter()

_MAX_ITERATIONS = 10


def _stream_ndjson(
    query_text: str,
    google_token: Optional[str],
    api_key: Optional[str],
    start: float,
) -> Iterator[str]:
    from pdbq.agent.prompts import build_system_prompt

    client = anthropic.Anthropic(api_key=api_key or settings.anthropic_api_key)
    system_prompt = build_system_prompt()
    messages: list[dict] = [{"role": "user", "content": query_text}]
    last_sql: Optional[str] = None
    tool_call_count = 0

    _TOOL_STATUS = {
        "query_db": "Running SQL query...",
        "get_live_record": "Fetching live record from PeeringDB...",
        "render_report": "Rendering report...",
    }

    try:
        yield json.dumps({"type": "status", "text": "Searching PeeringDB data..."}) + "\n"
        for _ in range(_MAX_ITERATIONS):
            buffered: list[str] = []

            with client.messages.stream(
                model=settings.anthropic_model,
                max_tokens=8096,
                system=system_prompt,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    buffered.append(text)
                final_msg = stream.get_final_message()

            tool_use_blocks = [b for b in final_msg.content if b.type == "tool_use"]

            if not tool_use_blocks:
                # Final response — yield buffered tokens
                yield json.dumps({"type": "status", "text": "Generating answer..."}) + "\n"
                for text in buffered:
                    yield json.dumps({"type": "token", "text": text}) + "\n"
                break

            # Tool-use turn — process tools, don't emit buffered tokens
            messages.append({"role": "assistant", "content": final_msg.content})
            tool_call_count += len(tool_use_blocks)
            tool_results = []

            for b in tool_use_blocks:
                yield json.dumps({"type": "status", "text": _TOOL_STATUS.get(b.name, "Working...")}) + "\n"
                tool_input = b.input
                if b.name == "query_db":
                    last_sql = tool_input.get("sql")
                if b.name == "export_to_sheets" and google_token and "user_token" not in tool_input:
                    tool_input = {**tool_input, "user_token": google_token}
                result = dispatch_tool(b.name, tool_input, api_key=api_key)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": b.id,
                    "content": json.dumps(result, default=str),
                })

            messages.append({"role": "user", "content": tool_results})

        else:
            yield json.dumps({
                "type": "token",
                "text": "The agent reached the maximum number of iterations without producing a final answer.",
            }) + "\n"

        elapsed_ms = int((time.monotonic() - start) * 1000)
        yield json.dumps({
            "type": "metadata",
            "sql_executed": last_sql,
            "tool_calls": tool_call_count,
            "elapsed_ms": elapsed_ms,
        }) + "\n"

    except Exception as exc:
        yield json.dumps({"type": "error", "message": str(exc)}) + "\n"


@router.post("/query", response_model=QueryResponse, dependencies=[Depends(require_api_key)])
async def query(
    request: QueryRequest,
    x_anthropic_key: Optional[str] = Header(default=None),
) -> QueryResponse:
    start = time.monotonic()
    resolved_key = x_anthropic_key or os.environ.get("ANTHROPIC_API_KEY")

    if request.stream:
        return StreamingResponse(
            _stream_ndjson(request.query, request.google_token, resolved_key, start),
            media_type="text/plain",
        )

    result = run_agent(request.query, google_token=request.google_token, api_key=resolved_key)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    return QueryResponse(
        answer=result.answer,
        sql_executed=result.sql_executed,
        tool_calls=result.tool_calls,
        elapsed_ms=elapsed_ms,
    )
