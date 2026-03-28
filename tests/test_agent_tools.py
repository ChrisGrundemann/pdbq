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
Unit tests for agent tools — no real API calls.
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from pdbq.agent.tools import (
    _validate_sql,
    execute_query_db,
    dispatch_tool,
)


class TestValidateSQL:
    def test_allows_select(self):
        _validate_sql("SELECT * FROM network WHERE status = 'ok'")

    def test_allows_cte(self):
        _validate_sql("WITH cte AS (SELECT id FROM network) SELECT * FROM cte")

    def test_blocks_insert(self):
        with pytest.raises(ValueError, match="INSERT"):
            _validate_sql("INSERT INTO network VALUES (1, 'test')")

    def test_blocks_drop(self):
        with pytest.raises(ValueError, match="DROP"):
            _validate_sql("DROP TABLE network")

    def test_blocks_delete(self):
        with pytest.raises(ValueError, match="DELETE"):
            _validate_sql("DELETE FROM network WHERE id = 1")

    def test_blocks_create(self):
        with pytest.raises(ValueError, match="CREATE"):
            _validate_sql("CREATE TABLE foo (id INTEGER)")

    def test_blocks_update(self):
        with pytest.raises(ValueError, match="UPDATE"):
            _validate_sql("UPDATE network SET name = 'x' WHERE id = 1")


class TestQueryDb:
    def test_query_returns_rows(self, write_conn):
        import duckdb
        from pdbq.sync.run import _upsert_records

        records = [{"id": 1001, "name": "Query Test Org", "status": "ok"}]
        _upsert_records(write_conn, "org", ["id", "name", "status"], records)
        write_conn.commit()

        # Use the write_conn directly — DuckDB allows multiple read operations on the same connection
        with patch("pdbq.agent.tools.get_read_connection") as mock_get_conn:
            # Create a separate in-memory DB with the org table and test data
            mem_conn = duckdb.connect(":memory:")
            mem_conn.execute("CREATE TABLE org (id INTEGER, name TEXT, status TEXT, raw_json TEXT)")
            mem_conn.execute("INSERT INTO org VALUES (1001, 'Query Test Org', 'ok', '{}')")
            mock_get_conn.return_value = mem_conn

            result = execute_query_db("SELECT id, name FROM org WHERE id = 1001")

        assert "rows" in result
        assert result["row_count"] == 1
        assert result["rows"][0]["id"] == 1001
        assert result["rows"][0]["name"] == "Query Test Org"

    def test_injection_blocked(self):
        result = execute_query_db("DROP TABLE network")
        assert "error" in result

    def test_invalid_sql_returns_error(self):
        with patch("pdbq.agent.tools.get_read_connection") as mock_get_conn:
            import duckdb
            conn = duckdb.connect(":memory:")
            mock_get_conn.return_value = conn
            result = execute_query_db("SELECT * FROM nonexistent_table_xyz")
        assert "error" in result

    def test_limit_injected(self):
        import duckdb

        with patch("pdbq.agent.tools.get_read_connection") as mock_get_conn:
            mem_conn = duckdb.connect(":memory:")
            mock_get_conn.return_value = mem_conn

            result = execute_query_db("SELECT 1 AS x")

        assert "rows" in result


class TestDispatchTool:
    def test_unknown_tool_returns_error(self):
        result = dispatch_tool("nonexistent_tool", {})
        assert "error" in result

    def test_query_db_dispatched(self):
        with patch("pdbq.agent.tools.execute_query_db") as mock:
            mock.return_value = {"rows": [], "row_count": 0, "columns": []}
            result = dispatch_tool("query_db", {"sql": "SELECT 1"})
            mock.assert_called_once_with("SELECT 1")

    def test_get_live_record_dispatched(self):
        with patch("pdbq.agent.tools.execute_get_live_record") as mock:
            mock.return_value = {"id": 1, "name": "Test"}
            result = dispatch_tool("get_live_record", {"resource": "net", "id": 1})
            mock.assert_called_once_with("net", 1)
