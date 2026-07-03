"""
Fetch current price quotes from Yahoo Finance using the yfinance library.

We use yf.download() with period="2d" — this makes ONE batch HTTP request
for all symbols and returns the last two trading days, which is what we
need to compute the day's percent change.

Trade-offs:
  - Free, no API key, unlimited-ish rate limit.
  - Unofficial scraper — Yahoo can (rarely) change their format.
  - Prices are typically 15-min delayed for retail feeds.
"""

from __future__ import annotations

import logging
from typing import Iterable

import yfinance as yf

log = logging.getLogger(__name__)


def fetch_quotes(symbols: Iterable[str]) -> list[dict]:
    """
    Return a list of {symbol, current_price, day_change_pct} dicts.

    Symbols that fail (missing data, delisted, etc.) are logged and skipped
    — the run does not crash. Callers should treat this as best-effort.
    """
    symbols = list(symbols)
    if not symbols:
        return []

    log.info("Downloading quotes for %d symbols", len(symbols))
    data = yf.download(
        tickers=symbols,
        period="2d",
        interval="1d",
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=True,
    )

    quotes: list[dict] = []
    for symbol in symbols:
        try:
            # When multiple tickers are downloaded, columns are MultiIndex
            # keyed by symbol. When only one, it's a flat DataFrame.
            frame = data[symbol] if len(symbols) > 1 else data
            closes = frame["Close"].dropna()

            if len(closes) < 2:
                log.warning("%s: not enough data (got %d closes)", symbol, len(closes))
                continue

            current = float(closes.iloc[-1])
            previous = float(closes.iloc[-2])
            change_pct = ((current - previous) / previous) * 100.0 if previous else 0.0

            quotes.append({
                "symbol": symbol,
                "current_price": round(current, 2),
                "day_change_pct": round(change_pct, 2),
            })
        except Exception as e:  # noqa: BLE001
            log.warning("%s: fetch failed — %s", symbol, e)

    log.info("Successfully fetched %d / %d quotes", len(quotes), len(symbols))
    return quotes
