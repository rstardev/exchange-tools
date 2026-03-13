from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type


class HttpClient:
    def __init__(self, base_url: str, timeout_s: float = 10.0):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout_s)

    async def aclose(self) -> None:
        await self._client.aclose()

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=0.3, max=3.0),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError)),
    )
    async def get_json(self, path: str, params: dict | None = None) -> dict:
        r = await self._client.get(path, params=params)
        r.raise_for_status()
        return r.json()
