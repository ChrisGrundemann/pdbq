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
import re

from fastapi import APIRouter, Depends, HTTPException

from pdbq.agent.core import run_agent
from pdbq.agent.sheets import exchange_auth_code
from pdbq.api.auth import require_api_key
from pdbq.api.models import ExportSheetsRequest, ExportSheetsResponse

router = APIRouter()

_SAFE_TOKEN_RE = re.compile(r'^[a-zA-Z0-9_-]{1,128}$')


@router.post("/export/sheets", response_model=ExportSheetsResponse, dependencies=[Depends(require_api_key)])
async def export_to_sheets(request: ExportSheetsRequest) -> ExportSheetsResponse:
    # Validate google_token before it reaches the filesystem
    if request.google_token and not _SAFE_TOKEN_RE.match(request.google_token):
        raise HTTPException(status_code=400, detail="Invalid google_token format")
    user_token = request.google_token
    if request.google_auth_code and not user_token:
        import secrets
        user_token = secrets.token_hex(16)
        exchange_auth_code(request.google_auth_code, user_token)

    if not user_token:
        raise HTTPException(status_code=400, detail="google_auth_code or google_token is required")

    result = run_agent(request.query, google_token=user_token)

    # Look for a sheet URL in the tool calls
    sheet_url = None
    for call in result.tool_calls:
        if call.get("tool") == "export_to_sheets":
            res = call.get("result", {})
            if "sheet_url" in res:
                sheet_url = res["sheet_url"]
                break

    if not sheet_url:
        raise HTTPException(
            status_code=500,
            detail="Agent did not produce a Sheets export. The query may not have returned exportable data.",
        )

    return ExportSheetsResponse(sheet_url=sheet_url)
