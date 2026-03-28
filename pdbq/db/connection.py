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
from pathlib import Path

import duckdb

from pdbq.config import settings


def get_write_connection() -> duckdb.DuckDBPyConnection:
    """Open a fresh read-write DuckDB connection.

    Callers are responsible for closing it when done.  A new connection is
    opened on every call so the write lock is released as soon as the caller
    closes it — no shared singleton that lingers between sync runs.
    """
    conn = duckdb.connect(settings.duckdb_path_abs)
    _init_schema(conn)
    return conn


def get_read_connection() -> duckdb.DuckDBPyConnection:
    """Open a fresh read-only DuckDB connection. Used by the API and agent.

    read_only=True does not acquire an exclusive lock, so these connections
    co-exist safely with a write connection held by a concurrent sync.
    Callers are responsible for closing it when done.
    """
    return duckdb.connect(settings.duckdb_path_abs, read_only=True)


def _init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    raw = schema_path.read_text()
    # Strip comment lines before splitting on ; so semicolons in comments don't
    # produce spurious empty statements.
    lines = [line for line in raw.splitlines() if not line.strip().startswith("--")]
    sql = "\n".join(lines)
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(statement)


def get_schema_sql() -> str:
    schema_path = Path(__file__).parent / "schema.sql"
    return schema_path.read_text()
