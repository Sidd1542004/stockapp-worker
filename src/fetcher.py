"""
Fetch current price quotes AND key fundamentals from Yahoo Finance.

Phase 5 update: in addition to price + day change, we now pull market cap,
trailing P/E, and dividend yield so the screener can filter on them with a
fast database query.

We still batch the price download in one request (fast). Fundamentals are
fetched per-symbol via yf.Ticker().info, which is slower, so we do it in a
thread pool with a modest worker count to stay polite to Yahoo.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

import yfinance as yf

log = logging.getLogger(__name__)


def _fetch_prices(symbols: list[str]) -> dict[str, dict]:
    """Batch-download 2 days of closes to compute price + day change."""
    log.info("Downloading prices for %d symbols", len(symbols))
    data = yf.download(
        tickers=symbols,
        period="2d",
        interval="1d",
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=True,
    )

    out: dict[str, dict] = {}
    for symbol in symbols:
        try:
            frame = data[symbol] if len(symbols) > 1 else data
            closes = frame["Close"].dropna()
            if len(closes) < 2:
                log.warning("%s: not enough price data", symbol)
                continue
            current = float(closes.iloc[-1])
            previous = float(closes.iloc[-2])
            change_pct = ((current - previous) / previous) * 100.0 if previous else 0.0
            out[symbol] = {
                "current_price": round(current, 2),
                "day_change_pct": round(change_pct, 2),
            }
        except Exception as e:  # noqa: BLE001
            log.warning("%s: price parse failed — %s", symbol, e)
    return out


def _fetch_fundamentals_one(symbol: str) -> dict | None:
    """Pull market cap, P/E, dividend yield for one symbol."""
    try:
        info = yf.Ticker(symbol).info
        return {
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": _normalize_yield(info.get("dividendYield")),
        }
    except Exception as e:  # noqa: BLE001
        log.warning("%s: fundamentals fetch failed — %s", symbol, e)
        return None


def _normalize_yield(value) -> float | None:
    """
    Normalize dividend yield to a FRACTION (0.02 == 2%).

    Yahoo has historically been inconsistent here — sometimes returning a
    fraction (0.02) and sometimes a percentage (2.0). We standardize on the
    fraction, which is what the UI and screener expect. Heuristic: a yield
    above 1 (i.e. >100%) is almost certainly a percentage, so divide by 100.
    Real dividend yields above 100% don't exist in practice.
    """
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    return v / 100.0 if v > 1 else v


def fetch_quotes(symbols: Iterable[str]) -> list[dict]:
    """
    Return a list of dicts with price + fundamentals for each symbol.

    Each dict: {symbol, current_price, day_change_pct, market_cap, pe_ratio,
    dividend_yield}. Missing fundamentals are left as None — the screener and
    UI handle nulls gracefully.
    """
    symbols = list(symbols)
    if not symbols:
        return []

    prices = _fetch_prices(symbols)

    # Fetch fundamentals concurrently (bounded pool).
    log.info("Fetching fundamentals for %d symbols", len(prices))
    fundamentals: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(_fetch_fundamentals_one, sym): sym for sym in prices
        }
        for fut in as_completed(futures):
            sym = futures[fut]
            result = fut.result()
            if result:
                fundamentals[sym] = result

    quotes: list[dict] = []
    for symbol, price in prices.items():
        f = fundamentals.get(symbol, {})
        quotes.append({
            "symbol": symbol,
            "current_price": price["current_price"],
            "day_change_pct": price["day_change_pct"],
            "market_cap": f.get("market_cap"),
            "pe_ratio": f.get("pe_ratio"),
            "dividend_yield": f.get("dividend_yield"),
        })

    log.info("Assembled %d quotes (%d with fundamentals)",
             len(quotes), len(fundamentals))
    return quotes
