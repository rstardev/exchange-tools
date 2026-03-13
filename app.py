from __future__ import annotations

import asyncio

import pandas as pd
import streamlit as st

from exchange_tools.config import DEFAULT_EXCHANGE, DEFAULT_INTERVAL
from exchange_tools.core.scanner import scan_exchange
from exchange_tools.exchanges.binance import BinanceFuturesClient
from exchange_tools.exchanges.bybit import BybitLinearClient


def _run(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.run(coro)
    return asyncio.run(coro)


@st.cache_data(ttl=60)
def _cached_symbols(exchange: str) -> list[str]:
    async def _fetch():
        if exchange == "bybit":
            c = BybitLinearClient()
        else:
            c = BinanceFuturesClient()
        try:
            return await c.list_usdt_perp_symbols()
        finally:
            await c.aclose()

    return _run(_fetch())


def main() -> None:
    st.set_page_config(page_title="Exchange Tools", layout="wide")
    st.title("Exchange Tools")

    with st.sidebar:
        st.subheader("Control panel")
        exchange = st.selectbox("Exchange", options=["binance", "bybit"], index=["binance", "bybit"].index(DEFAULT_EXCHANGE))
        interval = st.selectbox(
            "Candle interval",
            options=["1m", "5m", "15m", "1h", "4h", "12h", "1d"],
            index=["1m", "5m", "15m", "1h", "4h", "12h", "1d"].index(DEFAULT_INTERVAL),
        )
        include_funding = st.checkbox("Include funding rate", value=True)
        include_oi = st.checkbox("Include open interest", value=True)

        st.divider()
        st.subheader("Filtering")
        min_price_change = st.number_input("Min price change % (e.g. -5)", value=0.0, step=0.5)
        filter_price_enabled = st.checkbox("Enable price filter", value=False)
        min_volume_change = st.number_input("Min volume change % (e.g. 100)", value=0.0, step=5.0)
        filter_volume_enabled = st.checkbox("Enable volume filter", value=False)

        st.divider()
        st.subheader("Sorting")
        sort_by = st.selectbox(
            "Order by",
            options=["volume_change_pct", "price_change_pct", "funding_rate_pct", "open_interest"],
            index=0,
        )
        sort_desc = st.checkbox("Descending", value=True)
        top_n = st.slider("Show top N", min_value=20, max_value=300, value=100, step=10)

        refresh = st.button("Refresh")

    if refresh:
        st.cache_data.clear()

    symbols = _cached_symbols(exchange)
    st.caption(f"{exchange}: {len(symbols)} USDT perpetual symbols")

    async def _scan():
        if exchange == "bybit":
            c = BybitLinearClient()
        else:
            c = BinanceFuturesClient()
        try:
            return await scan_exchange(
                c,
                interval=interval,
                symbols=symbols,
                include_funding=include_funding,
                include_oi=include_oi,
            )
        finally:
            await c.aclose()

    with st.spinner("Scanning…"):
        rows = _run(_scan())

    df = pd.DataFrame([r.__dict__ for r in rows])

    # Basic cleanup / typing
    for col in ["price_change_pct", "volume_change_pct", "funding_rate_pct", "open_interest", "magnet_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if filter_price_enabled:
        df = df[df["price_change_pct"].notna() & (df["price_change_pct"] <= min_price_change)]
    if filter_volume_enabled:
        df = df[df["volume_change_pct"].notna() & (df["volume_change_pct"] >= min_volume_change)]

    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=not sort_desc, na_position="last")

    df = df.head(top_n)

    # Display
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "price_change_pct": st.column_config.NumberColumn("Price %", format="%.2f"),
            "volume_change_pct": st.column_config.NumberColumn("Volume %", format="%.2f"),
            "funding_rate_pct": st.column_config.NumberColumn("Funding %", format="%.4f"),
            "open_interest": st.column_config.NumberColumn("Open interest", format="%.4f"),
            "magnet_score": st.column_config.NumberColumn("Magnet score", format="%.4f"),
        },
    )


if __name__ == "__main__":
    main()

