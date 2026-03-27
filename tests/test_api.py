"""
API endpoint tests using TestClient (no real agent/DB calls).
"""
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from pdbq.api.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    from pdbq.config import settings
    return {"Authorization": f"Bearer {settings.api_keys[0]}"}


class TestHealth:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestQueryEndpoint:
    def test_query_returns_answer(self, client, auth_headers):
        mock_result = MagicMock()
        mock_result.answer = "# Test Answer\n\nHere is the result."
        mock_result.sql_executed = ["SELECT 1"]
        mock_result.tool_calls = []

        with patch("pdbq.api.routers.query.run_agent", return_value=mock_result):
            response = client.post(
                "/query",
                json={"query": "How many networks are there?"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "# Test Answer\n\nHere is the result."
        assert data["sql_executed"] == ["SELECT 1"]

    def test_query_missing_body(self, client, auth_headers):
        response = client.post("/query", json={}, headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_query_in_production_requires_auth(self, client, monkeypatch):
        from pdbq.config import settings
        monkeypatch.setattr(settings, "environment", "production")

        response = client.post("/query", json={"query": "test"})
        assert response.status_code == 401

    def test_query_in_production_with_valid_key(self, client, monkeypatch):
        from pdbq.config import settings
        monkeypatch.setattr(settings, "environment", "production")

        mock_result = MagicMock()
        mock_result.answer = "Answer"
        mock_result.sql_executed = []
        mock_result.tool_calls = []

        with patch("pdbq.api.routers.query.run_agent", return_value=mock_result):
            response = client.post(
                "/query",
                json={"query": "test"},
                headers={"Authorization": f"Bearer {settings.api_keys[0]}"},
            )
        assert response.status_code == 200

    def test_byoc_passes_anthropic_key_to_run_agent(self, client, auth_headers):
        mock_result = MagicMock()
        mock_result.answer = "Answer"
        mock_result.sql_executed = []
        mock_result.tool_calls = []

        with patch("pdbq.api.routers.query.run_agent", return_value=mock_result) as mock_run:
            client.post(
                "/query",
                json={"query": "test"},
                headers={**auth_headers, "X-Anthropic-Key": "test-user-key"},
            )

        mock_run.assert_called_once_with(
            "test",
            google_token=None,
            api_key="test-user-key",
        )

    def test_stream_true_returns_ndjson(self, client, auth_headers):
        token_line = json.dumps({"type": "token", "text": "hello"}) + "\n"
        metadata_line = json.dumps({
            "type": "metadata",
            "sql_executed": None,
            "tool_calls": 0,
            "elapsed_ms": 100,
        }) + "\n"

        with patch(
            "pdbq.api.routers.query._stream_ndjson",
            return_value=iter([token_line, metadata_line]),
        ):
            response = client.post(
                "/query",
                json={"query": "test", "stream": True},
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        body = response.text
        assert token_line in body
        assert metadata_line in body

    def test_stream_false_returns_query_response_shape(self, client, auth_headers):
        mock_result = MagicMock()
        mock_result.answer = "Answer"
        mock_result.sql_executed = []
        mock_result.tool_calls = []

        with patch("pdbq.api.routers.query.run_agent", return_value=mock_result):
            response = client.post(
                "/query",
                json={"query": "test", "stream": False},
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "answer" in response.json()


class TestSyncStatus:
    def test_sync_status_requires_admin_key(self, client):
        response = client.get("/sync/status")
        assert response.status_code == 401

    def test_sync_status_with_admin_key(self, client):
        from pdbq.config import settings

        # get_read_connection is imported inside the function body, patch at source
        with patch("pdbq.db.connection.get_read_connection") as mock_get_conn:
            mock_c = MagicMock()
            mock_c.execute.return_value.fetchall.return_value = []
            mock_c.close = MagicMock()
            mock_get_conn.return_value = mock_c

            response = client.get(
                "/sync/status",
                headers={"Authorization": f"Bearer {settings.admin_api_key}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "tables" in data
        assert "db_size_mb" in data
