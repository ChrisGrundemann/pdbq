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

    # A request carrying its own Anthropic key is self-funding — pass through.
    # The Anthropic API itself will reject invalid keys; no need to validate here.
    if request.headers.get("X-Anthropic-Key", "").strip():
        return

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
