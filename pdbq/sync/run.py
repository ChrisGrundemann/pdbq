"""
Sync entrypoint: fetch all PeeringDB objects and upsert into DuckDB.

Usage:
    python -m pdbq.sync.run             # full sync
    python -m pdbq.sync.run --incremental
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import duckdb

from pdbq.db.connection import get_write_connection
from pdbq.sync.client import PeeringDBClient

logger = logging.getLogger(__name__)

# Map: (peeringdb_endpoint, table_name, [column_names_in_order])
RESOURCES: List[Tuple[str, str, List[str]]] = [
    (
        "org",
        "org",
        ["id", "name", "website", "status", "created", "updated"],
    ),
    (
        "net",
        "network",
        [
            "id", "org_id", "asn", "name", "aka", "website",
            "info_type", "info_prefixes4", "info_prefixes6",
            "policy_general", "policy_locations", "policy_ratio", "policy_contracts",
            "status", "created", "updated",
        ],
    ),
    (
        "ix",
        "ix",
        [
            "id", "org_id", "name", "name_long", "country", "city",
            "region_continent", "media", "notes", "status", "created", "updated",
        ],
    ),
    (
        "fac",
        "facility",
        [
            "id", "org_id", "name", "aka", "website", "city", "state", "zipcode",
            "country", "clli", "rencode", "npanxx", "tech",
            "sales_email", "sales_phone", "tech_email", "tech_phone",
            "status", "created", "updated",
        ],
    ),
    (
        "ixlan",
        "ixlan",
        ["id", "ix_id", "name", "descr", "status", "created", "updated"],
    ),
    (
        "ixpfx",
        "ixpfx",
        ["id", "ixlan_id", "prefix", "protocol", "in_dfz", "status", "created", "updated"],
    ),
    (
        "netixlan",
        "netixlan",
        [
            "id", "net_id", "ixlan_id", "asn", "ipaddr4", "ipaddr6",
            "speed", "is_rs_peer", "operational", "status", "created", "updated",
        ],
    ),
    (
        "netfac",
        "netfac",
        [
            "id", "net_id", "fac_id", "local_asn",
            "avail_sonet", "avail_ethernet", "avail_atm",
            "status", "created", "updated",
        ],
    ),
    (
        "poc",
        "poc",
        [
            "id", "net_id", "role", "visible", "name", "phone", "email", "url",
            "status", "created", "updated",
        ],
    ),
    (
        "carrier",
        "carrier",
        ["id", "org_id", "name", "aka", "website", "status", "created", "updated"],
    ),
    (
        "ixfac",
        "ixfac",
        ["id", "ix_id", "fac_id", "status", "created", "updated"],
    ),
    (
        "carrierfac",
        "carrierfac",
        ["id", "carrier_id", "fac_id", "status", "created", "updated"],
    ),
    (
        "campus",
        "campus",
        ["id", "org_id", "name", "aka", "website", "status", "created", "updated"],
    ),
]


def _get_last_synced(conn: duckdb.DuckDBPyConnection, resource: str) -> Optional[datetime]:
    row = conn.execute(
        "SELECT last_synced_at FROM sync_meta WHERE resource = ?", [resource]
    ).fetchone()
    if row and row[0]:
        return row[0]
    return None


def _upsert_records(
    conn: duckdb.DuckDBPyConnection,
    table: str,
    columns: List[str],
    records: List[Dict[str, Any]],
) -> int:
    if not records:
        return 0

    all_columns = columns + ["raw_json"]
    placeholders = ", ".join(["?"] * len(all_columns))
    col_list = ", ".join(all_columns)
    # DuckDB uses INSERT OR REPLACE
    sql = f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})"

    rows = []
    skipped = 0
    for rec in records:
        if rec.get("id") is None:
            skipped += 1
            continue
        values = [rec.get(col) for col in columns]
        values.append(json.dumps(rec))
        rows.append(values)

    if skipped:
        logger.debug("Skipped %d record(s) in %s with null/missing id", skipped, table)
    if not rows:
        return 0

    conn.executemany(sql, rows)
    return len(rows)


def _update_sync_meta(
    conn: duckdb.DuckDBPyConnection,
    resource: str,
    count: int,
    synced_at: datetime,
) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO sync_meta (resource, last_synced_at, record_count)
        VALUES (?, ?, ?)
        """,
        [resource, synced_at, count],
    )


def sync_resource(
    conn: duckdb.DuckDBPyConnection,
    client: PeeringDBClient,
    endpoint: str,
    table: str,
    columns: List[str],
    incremental: bool = False,
) -> int:
    since: Optional[datetime] = None
    if incremental:
        since = _get_last_synced(conn, endpoint)
        if since:
            logger.info("Incremental sync for %s since %s", endpoint, since.isoformat())
        else:
            logger.info("No prior sync found for %s — performing full sync", endpoint)

    synced_at = datetime.now(tz=timezone.utc)
    total = 0
    batch: List[Dict[str, Any]] = []

    for record in client.iter_all(endpoint, since=since):
        batch.append(record)
        if len(batch) >= 1000:
            total += _upsert_records(conn, table, columns, batch)
            conn.commit()
            batch = []

    if batch:
        total += _upsert_records(conn, table, columns, batch)
        conn.commit()

    row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    _update_sync_meta(conn, endpoint, row_count, synced_at)
    conn.commit()
    logger.info("Synced %d records into %s (table total: %d)", total, table, row_count)
    return total


def sync_as_set(
    conn: duckdb.DuckDBPyConnection,
    client: PeeringDBClient,
) -> int:
    """Sync /as_set, which returns a single {asn: as_set_string} dict rather than paginated objects."""
    synced_at = datetime.now(tz=timezone.utc)
    data = client._get("as_set")
    payload = data.get("data", data)
    mapping: Dict[str, Any] = payload[0] if isinstance(payload, list) else payload

    rows = []
    for asn_str, as_set_name in mapping.items():
        try:
            net_id = int(asn_str)
        except (ValueError, TypeError):
            logger.debug("Skipping as_set entry with non-integer key: %r", asn_str)
            continue
        rows.append([net_id, str(as_set_name), json.dumps({asn_str: as_set_name})])

    if rows:
        conn.executemany(
            "INSERT OR REPLACE INTO as_set (net_id, name, raw_json) VALUES (?, ?, ?)",
            rows,
        )
        conn.commit()

    total = len(rows)
    row_count = conn.execute("SELECT COUNT(*) FROM as_set").fetchone()[0]
    _update_sync_meta(conn, "as_set", row_count, synced_at)
    conn.commit()
    logger.info("Synced %d records into as_set (table total: %d)", total, row_count)
    return total


def run_sync(incremental: bool = False, tables: Optional[List[str]] = None) -> Dict[str, int]:
    results: Dict[str, int] = {}
    conn = get_write_connection()
    try:
        resources = RESOURCES
        if tables:
            resources = [r for r in RESOURCES if r[1] in tables]

        with PeeringDBClient() as client:
            for endpoint, table, columns in resources:
                try:
                    count = sync_resource(conn, client, endpoint, table, columns, incremental)
                    results[endpoint] = count
                except Exception as exc:
                    logger.error("Failed to sync %s: %s", endpoint, exc, exc_info=True)
                    results[endpoint] = -1

            if not tables or "as_set" in tables:
                try:
                    results["as_set"] = sync_as_set(conn, client)
                except Exception as exc:
                    logger.error("Failed to sync as_set: %s", exc, exc_info=True)
                    results["as_set"] = -1
    finally:
        conn.close()

    return results


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Sync PeeringDB data into DuckDB")
    parser.add_argument("--incremental", action="store_true", help="Incremental sync")
    args = parser.parse_args()

    results = run_sync(incremental=args.incremental)
    for resource, count in results.items():
        status = "OK" if count >= 0 else "FAILED"
        print(f"{resource:20s} {count:8d}  {status}")
