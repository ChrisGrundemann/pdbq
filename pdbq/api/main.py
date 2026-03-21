import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pdbq.api.auth import require_api_key
from pdbq.api.routers import admin, export, query
from pdbq.config import settings

logger = logging.getLogger(__name__)

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
)

# CORS
if settings.is_development:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    origins = settings.allowed_origins_list
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
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
