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
Rate limiting for the pdbq API.

Two layers:
1. Per-IP request rate (slowapi) — applied only to community-key callers.
   BYOC callers (X-Anthropic-Key header present) are exempt because they
   pay their own Anthropic bill.

2. Daily request budget — a global cap on total community-key requests per
   calendar day, persisted in DuckDB so it survives Fly.io machine restarts.
   (Token-level tracking is a future enhancement once usage data is available.)
"""
import logging
from datetime import date, timezone, datetime
from typing import Optional

from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from pdbq.config import settings

logger = logging.getLogger(__name__)


def _community_key_identifier(request: Request) -> str:
    """
    Rate-limit key function for slowapi.
    Returns the client IP for community-key requests.
    Returns a constant string for BYOC requests so they share one unlimited bucket
    (effectively exempting them from per-IP limits).
    """
    if request.headers.get("X-Anthropic-Key"):
        return "byoc-exempt"
    # Respect X-Forwarded-For set by Fly.io's proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=_community_key_identifier)


def _is_byoc(request: Request) -> bool:
    return bool(request.headers.get("X-Anthropic-Key"))


def _get_today() -> str:
    return date.today().isoformat()


def _get_budget_connection():
    """Get a writable DuckDB connection for the budget ledger."""
    import duckdb
    from pdbq.config import settings as s
    return duckdb.connect(str(s.duckdb_path))


def _ensure_budget_table(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _rate_limit_budget (
            budget_date DATE PRIMARY KEY,
            request_count INTEGER NOT NULL DEFAULT 0
        )
    """)


def check_daily_budget(request: Request) -> None:
    """
    Check and increment the daily community-key request budget.
    Raises HTTP 429 if the daily budget is exhausted.
    BYOC callers are always exempt.
    No-op if daily_request_budget is 0 (unlimited) or rate_limit_enabled is False.
    """
    if not settings.rate_limit_enabled:
        return
    if _is_byoc(request):
        return
    if settings.daily_request_budget <= 0:
        return

    today = _get_today()
    try:
        conn = _get_budget_connection()
        try:
            _ensure_budget_table(conn)
            conn.execute("""
                INSERT INTO _rate_limit_budget (budget_date, request_count)
                VALUES (?, 1)
                ON CONFLICT (budget_date) DO UPDATE
                    SET request_count = _rate_limit_budget.request_count + 1
            """, [today])
            row = conn.execute(
                "SELECT request_count FROM _rate_limit_budget WHERE budget_date = ?",
                [today]
            ).fetchone()
            count = row[0] if row else 1
            if count > settings.daily_request_budget:
                logger.warning("Daily community-key budget exhausted (%d requests)", count)
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Daily community quota reached.",
                        "message": (
                            "The community API key has reached its daily request limit. "
                            "Bring your own Anthropic key (X-Anthropic-Key header) to continue."
                        ),
                    },
                )
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception as exc:
        # Budget tracking failure should not block the request
        logger.error("Rate limit budget check failed (non-blocking): %s", exc)
