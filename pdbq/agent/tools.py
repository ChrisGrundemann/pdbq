import json
import logging
import re
from typing import Any, Dict, List

import anthropic

from pdbq.config import settings
from pdbq.db.connection import get_read_connection
from pdbq.sync.client import PeeringDBClient

logger = logging.getLogger(__name__)

# Tool definitions for the Anthropic API
TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "query_db",
        "description": (
            "Execute a SQL SELECT query against the local DuckDB database containing PeeringDB data. "
            "Returns rows as a list of dicts. Always use this tool to look up data. "
            "Results are capped at 500 rows unless you include an explicit LIMIT."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A SQL SELECT statement to execute against the DuckDB database.",
                }
            },
            "required": ["sql"],
        },
    },
    {
        "name": "get_live_record",
        "description": (
            "Fetch a single record live from the PeeringDB REST API. "
            "Use this when you need the most current data for a specific object, "
            "or when the user asks for live/fresh data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "resource": {
                    "type": "string",
                    "description": "The PeeringDB resource type: net, ix, fac, org, netixlan, ixlan, ixpfx, netfac, poc, carrier, carrierfac, campus",
                },
                "id": {
                    "type": "integer",
                    "description": "The numeric ID of the record to fetch.",
                },
            },
            "required": ["resource", "id"],
        },
    },
    {
        "name": "export_to_sheets",
        "description": (
            "Export data to a new Google Sheet. "
            "Only use this when the user explicitly requests a Sheets export."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of dicts to export as rows.",
                },
                "title": {
                    "type": "string",
                    "description": "Title for the new Google Sheet.",
                },
                "user_token": {
                    "type": "string",
                    "description": "OAuth token identifier for the user. Required for Sheets export.",
                },
            },
            "required": ["data", "title"],
        },
    },
    {
        "name": "render_report",
        "description": (
            "Format raw data into a polished markdown report. "
            "Use this to produce a well-structured final answer from raw query results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "The raw data rows to format.",
                },
                "instructions": {
                    "type": "string",
                    "description": "Formatting instructions, e.g. 'format as a competitive analysis table'.",
                },
            },
            "required": ["data", "instructions"],
        },
    },
]

_SQL_DANGEROUS_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|GRANT|REVOKE|ATTACH|DETACH|COPY|EXPORT|IMPORT)\b",
    re.IGNORECASE,
)

MAX_ROWS = 500


def _validate_sql(sql: str) -> None:
    if _SQL_DANGEROUS_PATTERN.search(sql):
        raise ValueError(f"SQL contains disallowed statement type: {sql[:200]}")


def execute_query_db(sql: str) -> Dict[str, Any]:
    try:
        _validate_sql(sql)
        logger.info("Executing SQL: %s", sql[:500])
        conn = get_read_connection()
        try:
            # Inject LIMIT if not present
            sql_stripped = sql.rstrip().rstrip(";")
            if not re.search(r"\bLIMIT\b", sql_stripped, re.IGNORECASE):
                sql_stripped = f"{sql_stripped} LIMIT {MAX_ROWS}"
            rel = conn.execute(sql_stripped)
            columns = [desc[0] for desc in rel.description]
            rows = rel.fetchall()
            dicts = [dict(zip(columns, row)) for row in rows]
            return {"rows": dicts, "row_count": len(dicts), "columns": columns}
        finally:
            conn.close()
    except ValueError as exc:
        logger.warning("SQL validation failed: %s", exc)
        return {"error": str(exc), "sql": sql}
    except Exception as exc:
        logger.error("SQL execution error: %s | SQL: %s", exc, sql)
        return {"error": str(exc), "sql": sql}


def execute_get_live_record(resource: str, record_id: int) -> Dict[str, Any]:
    try:
        with PeeringDBClient() as client:
            return client.get_record(resource, record_id)
    except Exception as exc:
        logger.error("Failed to fetch live record %s/%d: %s", resource, record_id, exc)
        return {"error": str(exc), "resource": resource, "id": record_id}


def execute_export_to_sheets(
    data: List[Dict[str, Any]],
    title: str,
    user_token: str | None = None,
) -> Dict[str, Any]:
    from pdbq.agent.sheets import export_data_to_sheets
    return export_data_to_sheets(data=data, title=title, user_token=user_token)


def execute_render_report(data: List[Dict[str, Any]], instructions: str) -> Dict[str, Any]:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    prompt = (
        f"Format the following data into a polished markdown report.\n\n"
        f"Instructions: {instructions}\n\n"
        f"Data:\n```json\n{json.dumps(data, indent=2, default=str)}\n```\n\n"
        f"Return only the markdown content."
    )
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    markdown = response.content[0].text if response.content else ""
    return {"markdown": markdown}


def dispatch_tool(tool_name: str, tool_input: Dict[str, Any]) -> Any:
    if tool_name == "query_db":
        return execute_query_db(tool_input["sql"])
    elif tool_name == "get_live_record":
        return execute_get_live_record(tool_input["resource"], tool_input["id"])
    elif tool_name == "export_to_sheets":
        return execute_export_to_sheets(
            data=tool_input["data"],
            title=tool_input["title"],
            user_token=tool_input.get("user_token"),
        )
    elif tool_name == "render_report":
        return execute_render_report(tool_input["data"], tool_input["instructions"])
    else:
        return {"error": f"Unknown tool: {tool_name}"}
