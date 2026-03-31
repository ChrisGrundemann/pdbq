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
Unit tests for DuckDB error hint mapping in _duckdb_error_hint.
"""
import pytest

from pdbq.agent.tools import _duckdb_error_hint

_SQL = "SELECT 1"


class TestIntervalHints:
    def test_interval_in_message(self):
        hint = _duckdb_error_hint(Exception("invalid interval syntax"), _SQL)
        assert hint
        assert "INTERVAL" in hint

    def test_date_add_in_message(self):
        hint = _duckdb_error_hint(Exception("date_add is not supported"), _SQL)
        assert hint

    def test_date_sub_in_message(self):
        hint = _duckdb_error_hint(Exception("date_sub function not found"), _SQL)
        assert hint


class TestStrftimeHints:
    def test_strftime_in_message(self):
        hint = _duckdb_error_hint(Exception("strftime argument order is wrong"), _SQL)
        assert hint
        assert "strftime" in hint


class TestColumnHints:
    def test_referenced_column_not_found(self):
        hint = _duckdb_error_hint(Exception("referenced column not found"), _SQL)
        assert hint

    def test_column_not_found(self):
        hint = _duckdb_error_hint(Exception("column xyz not found"), _SQL)
        assert hint


class TestTableHints:
    def test_table_not_found(self):
        hint = _duckdb_error_hint(Exception("table foo not found"), _SQL)
        assert hint
        assert "network" in hint or "facility" in hint


class TestLimitSubqueryHints:
    def test_limit_in_subquery(self):
        hint = _duckdb_error_hint(Exception("limit in subquery not allowed"), _SQL)
        assert hint


class TestGroupByHints:
    def test_group_by_error(self):
        hint = _duckdb_error_hint(Exception("group by clause error"), _SQL)
        assert hint

    def test_aggregate_error(self):
        hint = _duckdb_error_hint(Exception("aggregate function not in group by"), _SQL)
        assert hint


class TestGenericSyntaxHints:
    def test_syntax_error(self):
        hint = _duckdb_error_hint(Exception("syntax error near SELECT"), _SQL)
        assert hint


class TestNoHint:
    def test_unrecognized_message_returns_empty(self):
        hint = _duckdb_error_hint(Exception("something completely unknown xyz"), _SQL)
        assert hint == ""
