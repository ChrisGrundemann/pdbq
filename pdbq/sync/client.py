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
import time
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
            params["since"] = int(since.timestamp())
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
            time.sleep(1)
            skip += PAGE_SIZE
            logger.debug("Fetched %d records from %s (skip=%d)", len(objects), resource, skip)

    def get_record(self, resource: str, record_id: int) -> Dict[str, Any]:
        data = self._get(f"{resource}/{record_id}", params={"depth": 1})
        return data.get("data", {})
