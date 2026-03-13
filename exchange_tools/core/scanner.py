from __future__ import annotations

import asyncio
from collections.abc import Iterable

from exchange_tools.config import MAX_CONCURRENCY
from exchange_tools.core.metrics import PairMetrics, pct_change
from exchange_tools.exchanges.types import ExchangeClient


def _parse_binance_candle(c: list) -> tuple[float, float, float]:
    # [openTime, open, high, low, close, volume, ...]
    close = float(c[4])
    volume = float(c[5])
    return close, volume, float(c[0])


def _parse_bybit_candle(c: list) -> tuple[float, float, float]:
    # [startTime, open, high, low, close, volume, turnover]
    close = float(c[4])
    volume = float(c[5])
    return close, volume, float(c[0])


async def scan_exchange(
    client: ExchangeClient,
    interval: str,
    symbols: Iterable[str],
    *,
    include_funding: bool = True,
    include_oi: bool = True,
) -> list[PairMetrics]:
    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async def one(symbol: str) -> PairMetrics | None:
        async with sem:
            candles = await client.get_last_two_candles(symbol, interval)
        if candles is None:
            return None
        prev, last = candles

        if client.name == "bybit":
            prev_close, prev_vol, _ = _parse_bybit_candle(prev)
            last_close, last_vol, _ = _parse_bybit_candle(last)
        else:
            prev_close, prev_vol, _ = _parse_binance_candle(prev)
            last_close, last_vol, _ = _parse_binance_candle(last)

        price_change = pct_change(prev_close, last_close)
        vol_change = pct_change(prev_vol, last_vol)

        funding: float | None = None
        oi: float | None = None

        if include_funding:
            try:
                async with sem:
                    funding = await client.get_funding_rate_pct(symbol)
            except Exception:
                funding = None

        if include_oi:
            try:
                async with sem:
                    oi = await client.get_open_interest(symbol)
            except Exception:
                oi = None

        return PairMetrics(
            exchange=client.name,
            symbol=symbol,
            interval=interval,
            price_change_pct=price_change,
            volume_change_pct=vol_change,
            funding_rate_pct=funding,
            open_interest=oi,
            magnet_score=None,
        )

    tasks = [one(s) for s in symbols]
    out = await asyncio.gather(*tasks, return_exceptions=False)
    return [x for x in out if x is not None]

