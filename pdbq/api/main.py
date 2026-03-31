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
import signal
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from pdbq.api.auth import require_api_key
from pdbq.api.rate_limit import limiter
from pdbq.api.routers import admin, export, query
from pdbq.config import settings

import sentry_sdk
from pdbq.config import settings as _settings_for_sentry

if _settings_for_sentry.sentry_dsn:
    sentry_sdk.init(
        dsn=_settings_for_sentry.sentry_dsn,
        environment=_settings_for_sentry.environment,  # 'production' or 'development'
        traces_sample_rate=_settings_for_sentry.sentry_traces_sample_rate,
        # Don't send PII — strip IP addresses and user agent from events
        send_default_pii=False,
    )

logger = logging.getLogger(__name__)

_SYNC_SHUTDOWN_TIMEOUT = 60  # seconds to wait for an in-progress sync on SIGTERM


def _run_scheduled_sync() -> None:
    from pdbq.sync.run import run_sync
    logger.info("Scheduled incremental sync starting")
    try:
        results = run_sync(incremental=True)
        logger.info("Scheduled incremental sync complete: %s", results)
    except Exception as exc:
        logger.error("Scheduled incremental sync failed: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Install a SIGTERM handler that waits for any background sync thread to finish
    # before allowing the process to exit.  uvicorn sends SIGTERM on graceful stop.
    original_handler = signal.getsignal(signal.SIGTERM)

    def _sigterm(signum, frame):
        logger.info("SIGTERM received — waiting up to %ds for background sync", _SYNC_SHUTDOWN_TIMEOUT)
        # admin._sync_thread is set by the background task wrapper when a sync is running.
        t = getattr(admin, "_sync_thread", None)
        if t is not None and t.is_alive():
            t.join(timeout=_SYNC_SHUTDOWN_TIMEOUT)
            if t.is_alive():
                logger.warning("Sync did not finish within %ds; proceeding with shutdown", _SYNC_SHUTDOWN_TIMEOUT)
        # Re-raise with the original handler so uvicorn can complete its own shutdown.
        if callable(original_handler):
            original_handler(signum, frame)
        else:
            raise SystemExit(0)

    signal.signal(signal.SIGTERM, _sigterm)

    scheduler = None
    if settings.sync_schedule_enabled:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler

            scheduler = BackgroundScheduler()
            scheduler.add_job(
                _run_scheduled_sync,
                trigger="interval",
                hours=settings.sync_schedule_interval_hours,
                max_instances=1,
            )
            scheduler.start()
            logger.warning(
                "Sync scheduler started — incremental sync every %d hour(s)",
                settings.sync_schedule_interval_hours,
            )
        except Exception as exc:
            logger.error("Failed to start sync scheduler: %s", exc)
            scheduler = None

    yield

    if scheduler is not None:
        try:
            scheduler.shutdown(wait=False)
            logger.info("Sync scheduler shut down")
        except Exception as exc:
            logger.error("Error shutting down sync scheduler: %s", exc)

    signal.signal(signal.SIGTERM, original_handler)

# Refuse to start in production with default credentials
if not settings.is_development:
    if settings.admin_api_key == "changeme-admin-key":
        raise RuntimeError(
            "ADMIN_API_KEY is set to the default value. "
            "Set a strong secret in your environment before starting in production."
        )
    if any(k.startswith("changeme") for k in settings.api_keys):
        raise RuntimeError(
            "PDBQ_API_KEYS contains a default 'changeme-*' value. "
            "Set strong secrets in your environment before starting in production."
        )

app = FastAPI(
    title="pdbq",
    description="Natural-language query agent over PeeringDB data",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://peeringdb.ai", # canonical (for fun)
        "https://www.peeringdb.ai",
        "https://pdbq.ai", # canonical (long term)
        "https://pdbq.io",
        "https://pdbq.org",
        "https://pdbq.app",
        "https://pdbq.pages.dev", # Cloudflare Pages preview URL
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Anthropic-Key"],
)

# Google OAuth routes
import re
import secrets as _secrets

from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import Depends, Request

_SAFE_TOKEN_RE = re.compile(r'^[a-zA-Z0-9_-]{1,128}$')


def _safe_token(value: str) -> str:
    """Validate that a user-supplied token/state is a safe filename component."""
    if not value or not _SAFE_TOKEN_RE.match(value):
        raise HTTPException(status_code=400, detail="Invalid token format")
    return value


@app.get("/auth/google", dependencies=[Depends(require_api_key)])
async def google_auth_redirect(state: str = ""):
    from pdbq.agent.sheets import get_auth_url
    if state:
        _safe_token(state)
    url = get_auth_url(state=state)
    return RedirectResponse(url)


@app.get("/auth/google/callback", dependencies=[Depends(require_api_key)])
async def google_auth_callback(request: Request, code: str, state: str = ""):
    from pdbq.agent.sheets import exchange_auth_code

    user_token = _safe_token(state) if state else _secrets.token_hex(16)
    exchange_auth_code(code, user_token)
    return JSONResponse({"user_token": user_token, "status": "authenticated"})


# Routers
app.include_router(query.router)
app.include_router(export.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
