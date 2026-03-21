"""
Shared test fixtures.
"""
import os
import tempfile
from pathlib import Path

import pytest

# Override DuckDB path before importing anything that uses it
_tmpdir = tempfile.mkdtemp()
os.environ.setdefault("DUCKDB_PATH", str(Path(_tmpdir) / "test.duckdb"))
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("PEERINGDB_API_KEY", "test-pdb-key")
os.environ.setdefault("ENVIRONMENT", "development")


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("db") / "test.duckdb"


@pytest.fixture
def write_conn(test_db_path, monkeypatch):
    import duckdb
    from pathlib import Path

    monkeypatch.setenv("DUCKDB_PATH", str(test_db_path))

    # Re-init settings and connection
    from pdbq.config import settings
    monkeypatch.setattr(settings, "duckdb_path", str(test_db_path))

    from pdbq.db import connection as conn_mod
    conn_mod._write_conn = None  # reset singleton

    conn = conn_mod.get_write_connection()
    yield conn
    conn_mod._write_conn = None
