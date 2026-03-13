from __future__ import annotations

from exchange_tools.config import BYBIT_BASE_URL
from exchange_tools.utils.http import HttpClient


_INTERVAL_MAP: dict[str, str] = {
    # Bybit v5 uses minutes as strings for kline interval
    "1m": "1",
    "3m": "3",
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240",
    "6h": "360",
    "12h": "720",
    "1d": "D",
}


class BybitLinearClient:
    name = "bybit"

    def __init__(self):
        self._http = HttpClient(BYBIT_BASE_URL)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def list_usdt_perp_symbols(self) -> list[str]:
        data = await self._http.get_json("/v5/market/instruments-info", params={"category": "linear"})
        result = data.get("result", {})
        items = result.get("list", []) or []
        out: list[str] = []
        for s in items:
            if s.get("quoteCoin") == "USDT" and s.get("status") in {"Trading", "trading"}:
                out.append(s["symbol"])
        return out

    async def get_last_two_candles(self, symbol: str, interval: str) -> tuple[list, list] | None:
        interval_param = _INTERVAL_MAP.get(interval)
        if interval_param is None:
            raise ValueError(f"Unsupported Bybit interval: {interval}")

        data = await self._http.get_json(
            "/v5/market/kline",
            params={"category": "linear", "symbol": symbol, "interval": interval_param, "limit": 2},
        )
        lst = (data.get("result", {}) or {}).get("list", [])
        if not isinstance(lst, list) or len(lst) < 2:
            return None
        # Bybit returns newest first typically; normalize to (prev, last) by sorting on startTime
        lst_sorted = sorted(lst, key=lambda x: int(x[0]))
        return lst_sorted[-2], lst_sorted[-1]

    async def get_funding_rate_pct(self, symbol: str) -> float | None:
        # v5 market/tickers includes fundingRate for linear category (as decimal fraction, e.g. 0.0001)
        data = await self._http.get_json("/v5/market/tickers", params={"category": "linear", "symbol": symbol})
        lst = (data.get("result", {}) or {}).get("list", [])
        if not lst:
            return None
        rate_str = lst[0].get("fundingRate")
        if rate_str is None:
            return None
        return float(rate_str) * 100.0

    async def get_open_interest(self, symbol: str) -> float | None:
        # v5 market/open-interest returns openInterest (contracts) for intervalTime
        data = await self._http.get_json(
            "/v5/market/open-interest",
            params={"category": "linear", "symbol": symbol, "intervalTime": "5min", "limit": 1},
        )
        lst = (data.get("result", {}) or {}).get("list", [])
        if not lst:
            return None
        oi_str = lst[0].get("openInterest")
        if oi_str is None:
            return None
        return float(oi_str)

