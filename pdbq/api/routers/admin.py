import os
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends

from pdbq.api.auth import require_admin_key
from pdbq.api.models import SyncStatusResponse, SyncTableStatus, SyncTriggerResponse
from pdbq.config import settings

router = APIRouter()


@router.get("/sync/status", response_model=SyncStatusResponse, dependencies=[Depends(require_admin_key)])
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

    return SyncStatusResponse(tables=tables, db_size_mb=db_size_mb)


def _run_sync_background(incremental: bool) -> None:
    from pdbq.sync.run import run_sync
    import logging

    logger = logging.getLogger(__name__)
    try:
        results = run_sync(incremental=incremental)
        logger.info("Background sync complete: %s", results)
    except Exception as exc:
        logger.error("Background sync failed: %s", exc)


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
