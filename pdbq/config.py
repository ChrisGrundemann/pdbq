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
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


def configure_logging(debug: bool = False) -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )
    for noisy in ("httpx", "httpcore", "anthropic", "markdown_it"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    if debug:
        logging.getLogger("pdbq").setLevel(logging.DEBUG)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Model provider
    model_provider: str = "anthropic"  # "anthropic" | "ollama"

    # Anthropic
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-5"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # PeeringDB
    peeringdb_api_key: str = ""
    peeringdb_base_url: str = "https://www.peeringdb.com/api"

    # DuckDB
    duckdb_path: str = "data/pdbq.duckdb"

    # Query history
    query_history_path: str = "data/query_history.jsonl"
    query_history_max_entries: int = 10000

    # Staleness warning
    sync_staleness_warn_hours: int = 24

    # Scheduled sync
    sync_schedule_enabled: bool = True
    sync_schedule_interval_hours: int = 6

    # Auth
    pdbq_api_keys: str = "changeme-key-1"
    admin_api_key: str = "changeme-admin-key"

    # Google OAuth
    google_client_secrets_path: str = "secrets/google_client_secrets.json"
    google_token_store_path: str = "data/google_tokens/"

    # CORS
    allowed_origins: str = ""

    # Environment
    environment: str = "development"

    @property
    def api_keys(self) -> List[str]:
        return [k.strip() for k in self.pdbq_api_keys.split(",") if k.strip()]

    @property
    def allowed_origins_list(self) -> List[str]:
        if not self.allowed_origins:
            return []
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def duckdb_path_abs(self) -> str:
        p = Path(self.duckdb_path)
        if not p.is_absolute():
            p = Path(__file__).parent.parent / p
        p.parent.mkdir(parents=True, exist_ok=True)
        return str(p)

    @property
    def query_history_path_abs(self) -> Path:
        p = Path(self.query_history_path)
        if not p.is_absolute():
            p = Path(__file__).parent.parent / p
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def google_token_store_path_abs(self) -> str:
        p = Path(self.google_token_store_path)
        if not p.is_absolute():
            p = Path(__file__).parent.parent / p
        p.mkdir(parents=True, exist_ok=True)
        return str(p)


settings = Settings()
