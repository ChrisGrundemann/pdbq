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


class SyncTriggerResponse(BaseModel):
    status: str
    message: str
