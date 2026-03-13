from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PairMetrics:
    exchange: str
    symbol: str
    interval: str

    price_change_pct: float | None
    volume_change_pct: float | None

    funding_rate_pct: float | None  # e.g. 0.01 means 0.01%
    open_interest: float | None

    magnet_score: float | None


def pct_change(prev: float, last: float) -> float | None:
    if prev == 0:
        return None
    return (last - prev) / prev * 100.0


def liquidity_magnet_score(current_price: float, liquidation_levels: list[dict]) -> float | None:
    """
    v4 concept scaffold.
    If you later provide real liquidation levels (price, size), we can compute
    the best/strongest magnet score near current price.
    """
    if not liquidation_levels:
        return None

    best: float | None = None
    for lvl in liquidation_levels:
        price = float(lvl["price"])
        size = float(lvl["size"])
        dist = abs(price - current_price)
        if dist <= 0:
            continue
        score = size / dist
        if best is None or score > best:
            best = score
    return best

