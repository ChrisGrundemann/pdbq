import logging
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException

from pdbq.api.auth import require_admin_key
from pdbq.api.models import SyncStatusResponse, SyncTableStatus, SyncTriggerResponse
from pdbq.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

_FLY_MACHINES_API = "https://api.machines.dev/v1"


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


def _build_machine_config(incremental: bool) -> dict:
    cmd = ["/app/.venv/bin/python", "sync/run.py"]
    if incremental:
        cmd.append("--incremental")

    config: dict = {
        "image": settings.fly_image_ref,
        "init": {"cmd": cmd},
        "auto_destroy": True,
        "restart": {"policy": "no"},
    }

    if settings.fly_volume_id:
        config["mounts"] = [{"volume": settings.fly_volume_id, "path": "/app/data"}]

    return config


@router.post("/sync/trigger", response_model=SyncTriggerResponse, dependencies=[Depends(require_admin_key)])
async def trigger_sync(incremental: bool = False) -> SyncTriggerResponse:
    if not settings.fly_api_token or not settings.fly_app_name or not settings.fly_image_ref:
        raise HTTPException(
            status_code=503,
            detail=(
                "Fly integration not configured. "
                "Set FLY_API_TOKEN, FLY_APP_NAME, and FLY_IMAGE_REF."
            ),
        )

    machine_config = _build_machine_config(incremental)
    payload = {
        "config": machine_config,
        "region": settings.fly_region,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{_FLY_MACHINES_API}/apps/{settings.fly_app_name}/machines",
            headers={
                "Authorization": f"Bearer {settings.fly_api_token}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if resp.status_code not in (200, 201):
        logger.error("Fly Machines API error %s: %s", resp.status_code, resp.text)
        raise HTTPException(
            status_code=502,
            detail=f"Failed to launch sync machine: {resp.status_code}",
        )

    machine_id = resp.json().get("id", "unknown")
    sync_type = "Incremental" if incremental else "Full"
    logger.info("Launched %s sync machine %s", sync_type.lower(), machine_id)

    return SyncTriggerResponse(
        status="accepted",
        message=f"{sync_type} sync started in machine {machine_id}.",
    )
