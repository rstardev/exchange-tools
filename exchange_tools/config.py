from __future__ import annotations

DEFAULT_EXCHANGE = "binance"
DEFAULT_INTERVAL = "4h"

# Change metrics are computed using the last 2 candles.
DEFAULT_LIMIT_CANDLES = 2

# Optional filtering thresholds (UI can override)
DEFAULT_MIN_PRICE_CHANGE_PCT = None  # e.g. -5.0
DEFAULT_MIN_VOLUME_CHANGE_PCT = None  # e.g. 100.0

# Concurrency limits (keep reasonable to avoid rate limits)
MAX_CONCURRENCY = 30

BINANCE_FUTURES_BASE_URL = "https://fapi.binance.com"
BYBIT_BASE_URL = "https://api.bybit.com"
