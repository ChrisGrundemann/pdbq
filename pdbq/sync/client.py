import logging
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from pdbq.config import settings

logger = logging.getLogger(__name__)

PAGE_SIZE = 500


class PeeringDBClient:
    def __init__(self) -> None:
        self.base_url = settings.peeringdb_base_url.rstrip("/")
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if settings.peeringdb_api_key:
            headers["Authorization"] = f"Api-Key {settings.peeringdb_api_key}"
        self._client = httpx.Client(
            headers=headers,
            timeout=60.0,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "PeeringDBClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def fetch_page(
        self,
        resource: str,
        skip: int = 0,
        since: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "limit": PAGE_SIZE,
            "skip": skip,
            "depth": 0,
        }
        if since is not None:
            params["since"] = since.strftime("%Y-%m-%dT%H:%M:%S")
        return self._get(resource, params=params)

    def iter_all(
        self,
        resource: str,
        since: Optional[datetime] = None,
    ) -> Iterator[Dict[str, Any]]:
        skip = 0
        while True:
            data = self.fetch_page(resource, skip=skip, since=since)
            objects: List[Dict[str, Any]] = data.get("data", [])
            if not objects:
                break
            for obj in objects:
                yield obj
            if len(objects) < PAGE_SIZE:
                break
            skip += PAGE_SIZE
            logger.debug("Fetched %d records from %s (skip=%d)", len(objects), resource, skip)

    def get_record(self, resource: str, record_id: int) -> Dict[str, Any]:
        data = self._get(f"{resource}/{record_id}", params={"depth": 1})
        return data.get("data", {})
