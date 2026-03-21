"""
Google Sheets OAuth + export logic.
"""
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pdbq.config import settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def _get_token_path(user_token: str) -> Path:
    store = Path(settings.google_token_store_path_abs)
    return store / f"{user_token}.json"


def _load_credentials(user_token: str):
    from google.oauth2.credentials import Credentials

    token_path = _get_token_path(user_token)
    if not token_path.exists():
        raise FileNotFoundError(f"No credentials found for token: {user_token}")
    return Credentials.from_authorized_user_file(str(token_path), SCOPES)


def _save_credentials(user_token: str, creds) -> None:
    token_path = _get_token_path(user_token)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())


def exchange_auth_code(auth_code: str, user_token: str) -> None:
    """Exchange an OAuth authorization code for credentials and store them."""
    from google_auth_oauthlib.flow import Flow

    secrets_path = settings.google_client_secrets_path
    flow = Flow.from_client_secrets_file(
        secrets_path,
        scopes=SCOPES,
        redirect_uri="postmessage",
    )
    flow.fetch_token(code=auth_code)
    _save_credentials(user_token, flow.credentials)


def get_auth_url(state: str = "") -> str:
    """Get the Google OAuth authorization URL."""
    from google_auth_oauthlib.flow import Flow

    secrets_path = settings.google_client_secrets_path
    flow = Flow.from_client_secrets_file(
        secrets_path,
        scopes=SCOPES,
        redirect_uri=f"{settings.peeringdb_base_url}/auth/google/callback",
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
    )
    return auth_url


def cli_oauth_flow() -> None:
    """Interactive OAuth flow for CLI usage — opens browser, stores token as 'cli'."""
    import gspread

    gc = gspread.oauth(
        credentials_filename=settings.google_client_secrets_path,
        authorized_user_filename=str(_get_token_path("cli")),
        scopes=SCOPES,
    )
    logger.info("CLI OAuth successful. Credentials stored.")
    return gc


def export_data_to_sheets(
    data: List[Dict[str, Any]],
    title: str,
    user_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new Google Sheet and populate it with data."""
    import gspread
    from google.auth.transport.requests import Request

    if not data:
        return {"error": "No data to export"}

    token = user_token or "cli"
    try:
        creds = _load_credentials(token)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            _save_credentials(token, creds)
    except FileNotFoundError:
        return {"error": f"No Google credentials found for token '{token}'. Please authenticate first."}

    gc = gspread.authorize(creds)
    sh = gc.create(title)

    worksheet = sh.get_worksheet(0)
    headers = list(data[0].keys())
    rows = [[str(row.get(h, "")) for h in headers] for row in data]

    worksheet.update([headers] + rows)

    sheet_url = f"https://docs.google.com/spreadsheets/d/{sh.id}"
    logger.info("Exported %d rows to Google Sheet: %s", len(data), sheet_url)

    return {"sheet_url": sheet_url, "sheet_id": sh.id}
