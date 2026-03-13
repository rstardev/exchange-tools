from __future__ import annotations

from typing import Protocol


class ExchangeClient(Protocol):
    name: str

    async def list_usdt_perp_symbols(self) -> list[str]:
        raise NotImplementedError

    async def get_last_two_candles(self, symbol: str, interval: str) -> tuple[list, list] | None:
        raise NotImplementedError

    async def get_funding_rate_pct(self, symbol: str) -> float | None:
        raise NotImplementedError

    async def get_open_interest(self, symbol: str) -> float | None:
        raise NotImplementedError

