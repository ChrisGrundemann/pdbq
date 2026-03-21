import hmac
import logging

from fastapi import HTTPException, Request, status

from pdbq.config import settings

logger = logging.getLogger(__name__)


async def require_api_key(request: Request) -> None:
    # Auth is ALWAYS enforced. Development mode only emits a warning — it does not skip auth.
    if settings.is_development:
        logger.warning(
            "ENVIRONMENT=development is active. Auth is still enforced. "
            "Do not deploy with this setting in production."
        )

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Expected: Bearer <key>",
        )
    key = auth_header.removeprefix("Bearer ").strip()
    if not any(hmac.compare_digest(key, valid) for valid in settings.api_keys):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


async def require_admin_key(request: Request) -> None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )
    key = auth_header.removeprefix("Bearer ").strip()
    if not hmac.compare_digest(key, settings.admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key",
        )
