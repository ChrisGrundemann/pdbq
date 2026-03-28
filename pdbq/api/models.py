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
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    stream: bool = False
    google_token: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sql_executed: List[str] = []
    tool_calls: List[Dict[str, Any]] = []
    elapsed_ms: int = 0


class ExportSheetsRequest(BaseModel):
    query: str
    google_auth_code: Optional[str] = None
    google_token: Optional[str] = None


class ExportSheetsResponse(BaseModel):
    sheet_url: str


class SyncTableStatus(BaseModel):
    resource: str
    last_synced_at: Optional[str] = None
    record_count: Optional[int] = None


class SyncStatusResponse(BaseModel):
    tables: List[SyncTableStatus]
    db_size_mb: float
    last_error: Optional[str] = None


class SyncTriggerResponse(BaseModel):
    status: str
    message: str
