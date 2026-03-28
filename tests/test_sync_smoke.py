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
Sync smoke tests — verify schema creation and upsert logic without hitting PeeringDB.
"""
import json

import pytest

from pdbq.db.connection import get_write_connection
from pdbq.sync.run import _upsert_records, _update_sync_meta, _get_last_synced


def test_schema_creates_tables(write_conn):
    tables = write_conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
    ).fetchall()
    table_names = {row[0] for row in tables}

    expected = {
        "org", "network", "ix", "facility", "ixlan", "ixpfx",
        "netixlan", "netfac", "poc", "carrier", "carrierfac", "campus", "sync_meta"
    }
    assert expected.issubset(table_names), f"Missing tables: {expected - table_names}"


def test_upsert_network_records(write_conn):
    records = [
        {
            "id": 1,
            "org_id": 100,
            "asn": 64496,
            "name": "Test Network",
            "status": "ok",
            "info_prefixes4": 10,
            "info_prefixes6": 5,
        },
        {
            "id": 2,
            "org_id": 101,
            "asn": 64497,
            "name": "Another Network",
            "status": "ok",
            "info_prefixes4": 20,
            "info_prefixes6": 0,
        },
    ]
    columns = ["id", "org_id", "asn", "name", "status", "info_prefixes4", "info_prefixes6"]
    count = _upsert_records(write_conn, "network", columns, records)
    write_conn.commit()

    assert count == 2
    rows = write_conn.execute("SELECT id, asn, name FROM network ORDER BY id").fetchall()
    assert len(rows) == 2
    assert rows[0] == (1, 64496, "Test Network")
    assert rows[1] == (2, 64497, "Another Network")


def test_upsert_is_idempotent(write_conn):
    records = [{"id": 10, "org_id": 200, "asn": 65000, "name": "Idempotent Net", "status": "ok"}]
    columns = ["id", "org_id", "asn", "name", "status"]

    _upsert_records(write_conn, "network", columns, records)
    write_conn.commit()
    _upsert_records(write_conn, "network", columns, records)
    write_conn.commit()

    rows = write_conn.execute("SELECT id FROM network WHERE id = 10").fetchall()
    assert len(rows) == 1


def test_raw_json_stored(write_conn):
    record = {"id": 99, "name": "JSON Test Org", "status": "ok", "extra_field": "preserved"}
    _upsert_records(write_conn, "org", ["id", "name", "status"], [record])
    write_conn.commit()

    row = write_conn.execute("SELECT raw_json FROM org WHERE id = 99").fetchone()
    assert row is not None
    parsed = json.loads(row[0])
    assert parsed["extra_field"] == "preserved"


def test_sync_meta(write_conn):
    from datetime import datetime, timezone

    now = datetime.now(tz=timezone.utc)
    _update_sync_meta(write_conn, "net", 500, now)
    write_conn.commit()

    last = _get_last_synced(write_conn, "net")
    assert last is not None


def test_sync_meta_missing_resource(write_conn):
    result = _get_last_synced(write_conn, "nonexistent_resource")
    assert result is None
