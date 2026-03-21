import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from pdbq.agent.core import run_agent, stream_agent
from pdbq.api.auth import require_api_key
from pdbq.api.models import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse, dependencies=[Depends(require_api_key)])
async def query(request: QueryRequest) -> QueryResponse:
    start = time.monotonic()

    if request.stream:
        # For streaming, return a StreamingResponse
        def generate():
            for chunk in stream_agent(request.query, google_token=request.google_token):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")

    result = run_agent(request.query, google_token=request.google_token)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    return QueryResponse(
        answer=result.answer,
        sql_executed=result.sql_executed,
        tool_calls=result.tool_calls,
        elapsed_ms=elapsed_ms,
    )
