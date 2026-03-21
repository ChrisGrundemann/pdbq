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

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"

    # PeeringDB
    peeringdb_api_key: str = ""
    peeringdb_base_url: str = "https://www.peeringdb.com/api"

    # DuckDB
    duckdb_path: str = "data/pdbq.duckdb"

    # Query history
    query_history_path: str = "data/query_history.jsonl"
    query_history_max_entries: int = 10000

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

    # Fly.io (populated automatically by the Fly runtime)
    fly_api_token: str = ""   # FLY_API_TOKEN — set as a Fly secret
    fly_app_name: str = ""    # FLY_APP_NAME  — injected by Fly
    fly_image_ref: str = ""   # FLY_IMAGE_REF — injected by Fly
    fly_volume_id: str = ""   # optional: volume ID to mount in the sync machine
    fly_region: str = "dfw"   # region for the ephemeral sync machine

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
