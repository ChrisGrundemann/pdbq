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
Unit tests for rate_limit helpers — no real DuckDB connections or HTTP requests.
"""
from unittest.mock import MagicMock, patch

import pytest

from pdbq.api.rate_limit import (
    _community_key_identifier,
    _is_byoc,
    check_daily_budget,
)
from pdbq.config import settings


def make_request(headers: dict) -> MagicMock:
    request = MagicMock()
    request.headers = headers
    return request


class TestIsByoc:
    def test_returns_true_when_key_present(self):
        request = make_request({"X-Anthropic-Key": "sk-ant-test"})
        assert _is_byoc(request) is True

    def test_returns_false_when_key_absent(self):
        request = make_request({})
        assert _is_byoc(request) is False

    def test_returns_false_when_key_is_empty_string(self):
        request = make_request({"X-Anthropic-Key": ""})
        assert _is_byoc(request) is False


class TestCommunityKeyIdentifier:
    def test_byoc_returns_exempt_constant(self):
        request = make_request({"X-Anthropic-Key": "sk-ant-test"})
        assert _community_key_identifier(request) == "byoc-exempt"

    def test_forwarded_for_returns_first_ip(self):
        request = make_request({"X-Forwarded-For": "1.2.3.4, 5.6.7.8"})
        assert _community_key_identifier(request) == "1.2.3.4"

    def test_falls_back_to_get_remote_address(self):
        request = make_request({})
        with patch("pdbq.api.rate_limit.get_remote_address", return_value="9.9.9.9") as mock_gra:
            result = _community_key_identifier(request)
        assert result == "9.9.9.9"
        mock_gra.assert_called_once_with(request)


class TestCheckDailyBudgetEarlyExits:
    def test_no_op_when_rate_limit_disabled(self, monkeypatch):
        monkeypatch.setattr(settings, "rate_limit_enabled", False)
        request = make_request({})
        with patch("pdbq.api.rate_limit._get_budget_connection") as mock_conn:
            check_daily_budget(request)
        mock_conn.assert_not_called()

    def test_no_op_for_byoc_request(self, monkeypatch):
        monkeypatch.setattr(settings, "rate_limit_enabled", True)
        monkeypatch.setattr(settings, "daily_request_budget", 1)
        request = make_request({"X-Anthropic-Key": "sk-ant-test"})
        with patch("pdbq.api.rate_limit._get_budget_connection") as mock_conn:
            check_daily_budget(request)
        mock_conn.assert_not_called()

    def test_no_op_when_budget_is_zero(self, monkeypatch):
        monkeypatch.setattr(settings, "rate_limit_enabled", True)
        monkeypatch.setattr(settings, "daily_request_budget", 0)
        request = make_request({})
        with patch("pdbq.api.rate_limit._get_budget_connection") as mock_conn:
            check_daily_budget(request)
        mock_conn.assert_not_called()
