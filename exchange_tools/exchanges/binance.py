from __future__ import annotations

from exchange_tools.config import BINANCE_FUTURES_BASE_URL
from exchange_tools.utils.http import HttpClient


_INTERVAL_MAP: dict[str, str] = {
    "1m": "1m",
    "3m": "3m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "2h": "2h",
    "4h": "4h",
    "6h": "6h",
    "8h": "8h",
    "12h": "12h",
    "1d": "1d",
}


class BinanceFuturesClient:
    name = "binance"

    def __init__(self):
        self._http = HttpClient(BINANCE_FUTURES_BASE_URL)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def list_usdt_perp_symbols(self) -> list[str]:
        data = await self._http.get_json("/fapi/v1/exchangeInfo")
        out: list[str] = []
        for s in data.get("symbols", []):
            if s.get("quoteAsset") == "USDT" and s.get("contractType") == "PERPETUAL" and s.get("status") == "TRADING":
                out.append(s["symbol"])
        return out

    async def get_last_two_candles(self, symbol: str, interval: str) -> tuple[list, list] | None:
        interval_param = _INTERVAL_MAP.get(interval)
        if interval_param is None:
            raise ValueError(f"Unsupported Binance interval: {interval}")

        data = await self._http.get_json(
            "/fapi/v1/klines",
            params={"symbol": symbol, "interval": interval_param, "limit": 2},
        )
        if not isinstance(data, list) or len(data) < 2:
            return None
        return data[-2], data[-1]

    async def get_funding_rate_pct(self, symbol: str) -> float | None:
        # /fapi/v1/premiumIndex returns lastFundingRate as decimal fraction (e.g. 0.0001 = 0.01%)
        data = await self._http.get_json("/fapi/v1/premiumIndex", params={"symbol": symbol})
        rate_str = data.get("lastFundingRate")
        if rate_str is None:
            return None
        rate = float(rate_str) * 100.0
        return rate

    async def get_open_interest(self, symbol: str) -> float | None:
        data = await self._http.get_json("/fapi/v1/openInterest", params={"symbol": symbol})
        oi_str = data.get("openInterest")
        if oi_str is None:
            return None
        return float(oi_str)

