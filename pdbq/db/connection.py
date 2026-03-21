from pathlib import Path
from typing import Optional

import duckdb

from pdbq.config import settings

_write_conn: Optional[duckdb.DuckDBPyConnection] = None


def get_write_connection() -> duckdb.DuckDBPyConnection:
    """Return a read-write DuckDB connection. Only the sync process should use this."""
    global _write_conn
    if _write_conn is None:
        _write_conn = duckdb.connect(settings.duckdb_path_abs)
        _init_schema(_write_conn)
    return _write_conn


def get_read_connection() -> duckdb.DuckDBPyConnection:
    """Return a read-only DuckDB connection. Used by the API and agent."""
    conn = duckdb.connect(settings.duckdb_path_abs, read_only=True)
    return conn


def _init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    sql = schema_path.read_text()
    # Execute each statement individually
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(statement)


def get_schema_sql() -> str:
    schema_path = Path(__file__).parent / "schema.sql"
    return schema_path.read_text()
