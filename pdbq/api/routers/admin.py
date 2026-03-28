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
import logging
import threading
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends

from pdbq.api.auth import require_admin_key
from pdbq.api.models import SyncStatusResponse, SyncTableStatus, SyncTriggerResponse
from pdbq.config import settings

router = APIRouter()

# Holds the currently-running sync thread so the SIGTERM handler in main.py can join it.
_sync_thread: threading.Thread | None = None
# Last error message from a background sync, cleared at the start of each run.
_last_sync_error: str | None = None


@router.get("/sync/status", response_model=SyncStatusResponse)
async def sync_status() -> SyncStatusResponse:
    from pdbq.db.connection import get_read_connection

    tables = []
    try:
        conn = get_read_connection()
        try:
            rows = conn.execute(
                "SELECT resource, last_synced_at, record_count FROM sync_meta ORDER BY resource"
            ).fetchall()
            for row in rows:
                tables.append(
                    SyncTableStatus(
                        resource=row[0],
                        last_synced_at=row[1].isoformat() if row[1] else None,
                        record_count=row[2],
                    )
                )
        finally:
            conn.close()
    except Exception:
        pass

    db_path = Path(settings.duckdb_path_abs)
    db_size_mb = round(db_path.stat().st_size / (1024 * 1024), 2) if db_path.exists() else 0.0

    return SyncStatusResponse(tables=tables, db_size_mb=db_size_mb, last_error=_last_sync_error)


def _run_sync_background(incremental: bool) -> None:
    global _sync_thread, _last_sync_error
    import logging

    from pdbq.sync.run import run_sync

    logger = logging.getLogger(__name__)
    _sync_thread = threading.current_thread()
    _last_sync_error = None
    try:
        results = run_sync(incremental=incremental)
        failed = {r: c for r, c in results.items() if c < 0}
        if failed:
            msg = f"Sync finished with failures: {', '.join(failed)}"
            logger.error(msg)
            _last_sync_error = msg
        else:
            logger.info("Background sync complete: %s", results)
    except Exception as exc:
        logger.error("Background sync raised an exception", exc_info=True)
        _last_sync_error = str(exc)
    finally:
        _sync_thread = None


@router.post("/sync/trigger", response_model=SyncTriggerResponse, dependencies=[Depends(require_admin_key)])
async def trigger_sync(
    background_tasks: BackgroundTasks,
    incremental: bool = False,
) -> SyncTriggerResponse:
    background_tasks.add_task(_run_sync_background, incremental)
    return SyncTriggerResponse(
        status="accepted",
        message=f"{'Incremental' if incremental else 'Full'} sync started in background.",
    )
